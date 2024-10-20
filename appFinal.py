import os
import time
import base64
import logging
import requests
import asyncio

from flask import Flask, request, Response
from transformers import pipeline
from botbuilder.schema import Activity, ActivityTypes, AttachmentLayoutTypes, HeroCard, CardImage
from botbuilder.core import (
    BotFrameworkAdapter, BotFrameworkAdapterSettings,
    ConversationState, MemoryStorage, ActivityHandler, TurnContext,
    MessageFactory, CardFactory
)
from botbuilder.dialogs import (
    Dialog, DialogSet, WaterfallDialog, WaterfallStepContext,
    TextPrompt, PromptOptions, DialogTurnStatus
)

# Retrieve Hugging Face API token from environment variable
hf_token = os.getenv("HUGGING_FACE_API_TOKEN")
if not hf_token:
    raise ValueError("HUGGING_FACE_API_TOKEN environment variable is not set")

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize Flask app
app = Flask(__name__)

# Initialize the Hugging Face pipeline for recipe generation
nlp = pipeline(
    "text2text-generation",
    model="flax-community/t5-recipe-generation",
    temperature=0.8,
    top_k=50
)

# Initialize the Bot Framework adapter settings
settings = BotFrameworkAdapterSettings("", "")
adapter = BotFrameworkAdapter(settings)

# State management setup
memory = MemoryStorage()
conversation_state = ConversationState(memory)

# Welcome message content
WELCOME_MESSAGE = (
    "Hello! Welcome to RecepAI. I can help you find recipes based on your ingredients. "
    "Type anything to begin."
)

class RecipeDialog(WaterfallDialog):
    def __init__(self, dialog_id: str):
        super().__init__(dialog_id, [
            self.ask_ingredient_step,
            self.suggest_recipe_step
        ])

    async def ask_ingredient_step(self, step_context: WaterfallStepContext):
        prompt = MessageFactory.text(
            "Please enter the ingredients you have (e.g., chicken, tomato, cheese)."
        )
        return await step_context.prompt(TextPrompt.__name__, PromptOptions(prompt=prompt))

    async def suggest_recipe_step(self, step_context: WaterfallStepContext):
        user_input = step_context.result

        # Generate three different recipe prompts
        recipe_prompts = [
            f"{user_input} recipe idea",
            f"Make a dish with {user_input}",
            f"Create a recipe using {user_input}"
        ]

        recipes = [nlp(prompt, max_length=100)[0]['generated_text'] for prompt in recipe_prompts]
        logging.info(f"Generated Recipes: {recipes}")

        attachments = self.create_recipe_cards(recipes)
        carousel_activity = Activity(
            type=ActivityTypes.message,
            attachment_layout=AttachmentLayoutTypes.carousel,
            attachments=attachments
        )

        await step_context.context.send_activity(carousel_activity)

        prompt = MessageFactory.text(
            "Would you like to search for more recipes? If so, please enter new ingredients."
        )
        return await step_context.replace_dialog(self.id, options=PromptOptions(prompt=prompt))

    def create_recipe_cards(self, recipes):
        attachments = []
        for recipe in recipes:
            title, ingredients, directions = self.extract_recipe_info(recipe)
            ingredients_str = ingredients.replace(", ", ",")

            image_data_url = self.generate_image(title)

            card = HeroCard(
                title=title,
                text=f"**Ingredients:**\n{ingredients_str}\n\n**Directions:**\n{directions}",
                images=[CardImage(url=image_data_url)],
            )

            attachments.append(CardFactory.hero_card(card))
        return attachments

    def extract_recipe_info(self, recipe):
        title, ingredients, directions = "Recipe", "N/A", "N/A"

        if 'title:' in recipe:
            title = recipe.split('title:')[1].split('ingredients:')[0].strip().upper()
        if 'ingredients:' in recipe:
            ingredients = recipe.split('ingredients:')[1].split('directions:')[0].strip()
        if 'directions:' in recipe:
            directions = recipe.split('directions:')[1].strip()

        return title, ingredients, directions

    def generate_image(self, prompt):
        api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        headers = {"Authorization": f"Bearer {hf_token}"}
        try:
            time.sleep(1)
            response = requests.post(api_url, headers=headers, json={"inputs": prompt}, timeout=30)
            response.raise_for_status()
            if response.status_code == 200:
                image_data = base64.b64encode(response.content).decode('utf-8')
                return f"data:image/png;base64,{image_data}"
            else:
                logging.error(f"API returned status code: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Error generating image: {str(e)}")
            return None

class RecipeBot(ActivityHandler):
    def __init__(self, conversation_state: ConversationState, dialog: Dialog):
        self.conversation_state = conversation_state
        self.dialog = dialog
        self.dialog_state_accessor = self.conversation_state.create_property("DialogState")

    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)
        await self.conversation_state.save_changes(turn_context)

        if turn_context.activity.type == ActivityTypes.conversation_update:
            if turn_context.activity.members_added:
                for member in turn_context.activity.members_added:
                    if member.id != turn_context.activity.recipient.id:
                        await turn_context.send_activity(MessageFactory.text(WELCOME_MESSAGE))

    async def on_message_activity(self, turn_context: TurnContext):
        dialog_set = DialogSet(self.dialog_state_accessor)
        dialog_set.add(TextPrompt(TextPrompt.__name__))
        dialog_set.add(self.dialog)

        dialog_context = await dialog_set.create_context(turn_context)
        result = await dialog_context.continue_dialog()

        if result.status == DialogTurnStatus.Empty:
            await dialog_context.begin_dialog(self.dialog.id)

# Initialize Dialogs and Bot
dialog = RecipeDialog("recipeDialog")
bot = RecipeBot(conversation_state, dialog)

# Define the Flask endpoint for bot messages
@app.route("/api/messages", methods=["POST"])
def messages_endpoint():
    body = request.json

    if not body:
        return Response("Request body is empty", status=400)

    activity = Activity().deserialize(body)

    async def call_bot():
        await adapter.process_activity(activity, "", bot.on_turn)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(call_bot())

    return Response(status=200)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, port=3978, threaded=False)