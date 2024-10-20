# RecepAI - AI-based Recipe Chatbot

RecepAI is an AI-driven chatbot designed to provide recipe suggestions based on user-input ingredients. It uses Microsoft's Bot Framework and Hugging Face models to generate and display recipe ideas, complete with ingredients and directions.

## Table of Contents
- [About the Project](#about-the-project)
- [Features](#features)
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Models Used](#models-used)
- [Resources](#resources)
- [License](#license)

## About the Project
RecepAI is built to help users discover new recipes using simple natural language inputs. The bot generates recipe ideas, extracts ingredients and directions, and presents them in a user-friendly carousel format. It also generates visual representations of recipes using the Stable Diffusion model.

## Features
- **Recipe Generation:** Suggests recipes based on the ingredients provided by the user.
- **Image Generation:** Uses a diffusion model to create images representing the generated recipes.
- **Stateful Conversations:** Keeps track of the conversation flow and recipe suggestions.
- **Carousel Display:** Displays recipe suggestions in an easy-to-read carousel format.

## Installation
Follow these steps to set up and run the project locally:

### Prerequisites
- Python 3.7 or later
- [Flask](https://flask.palletsprojects.com/)
- [Microsoft Bot Framework SDK for Python](https://github.com/microsoft/botbuilder-python)
- [Hugging Face Transformers](https://github.com/huggingface/transformers)
- [Microsoft Bot Emulator](https://github.com/microsoft/BotFramework-Emulator) (for testing locally)

### Steps
1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/recepai.git
    cd recepai
    ```

2. Create a virtual environment and activate it:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up the environment variables:
    - Add your Hugging Face API token to the environment:
      ```bash
      export HUGGING_FACE_API_TOKEN="your_hugging_face_api_token"
      ```

5. Run the Flask app:
    ```bash
    python app.py
    ```

6. Open the [Microsoft Bot Emulator](https://github.com/microsoft/BotFramework-Emulator) and connect it to the bot endpoint:
    ```
    http://localhost:3978/api/messages
    ```

## Getting Started
After setting up the bot, you can begin interacting with it through the Bot Emulator. Enter ingredients like "chicken, tomato, cheese" to receive recipe suggestions.

## Models Used
This project utilizes the following Hugging Face models:

### 1. Recipe Generation Model
- Model: [flax-community/t5-recipe-generation](https://huggingface.co/flax-community/t5-recipe-generation)
- Purpose: Generates recipe ideas based on provided ingredients.
- How it works: Takes a list of ingredients as input and returns recipe suggestions with ingredients and directions.

### 2. Image Generation Model
- Model: [runwayml/stable-diffusion-v1-5](https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5)
- Purpose: Creates visual representations of generated recipes.
- How it works: Takes a text prompt (recipe name or ingredients) and returns an image of the dish.

## Resources
- [Microsoft Chatbot Samples](https://github.com/microsoft/BotBuilder-Samples) - Explore various sample bots created using Microsoft's Bot Framework.
- [Microsoft Bot Framework Emulator](https://github.com/microsoft/BotFramework-Emulator) - A desktop application for testing and debugging chatbots built using the Bot Framework.

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Meet the Team

Aditya Nitin Bhagwat, 
Charlotte Eva Natalie Uddfors, 
Ramya Danappa, 
Shynitha Sudarshan Kotian, 
Sidhant Bansal


