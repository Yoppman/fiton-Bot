
# FitTON Telegram Bot

FitTON is a health-oriented Telegram bot designed to provide users with professional health advice. By integrating OpenAI's API capabilities, this bot offers personalized suggestions and analyses based on user interactions and uploaded photos. The bot is ideal for users seeking quick and professional feedback on their health and fitness journey.

## Features

- **Health Advice**: The bot responds to various health-related queries and provides tailored advice.
- **Photo Upload**: Users can upload images (e.g., meals, fitness activities), and the bot will analyze and give professional feedback based on the image contents.
- **AI Integration**: Powered by OpenAI, the bot ensures that the responses are not only intelligent but also context-aware, helping users make informed decisions.
- **Telegram Bot Commands**: Use simple commands to interact with the bot and receive immediate assistance.

Start interacting with the bot [here](https://t.me/Fit_ioBot).

## How It Works

1. Start a conversation with the bot by using the `/start` command.
2. You can ask health-related questions or upload a photo (e.g., a meal) for detailed feedback and advice.
3. The bot will process the request and return relevant suggestions, advice, or analysis.

## Prerequisites

- **Python 3.8 or higher**
- **Telegram Bot Token**: You will need to create a bot on Telegram and get the token to integrate it.
- **OpenAI API Key**: You must have an OpenAI API key to enable AI responses.

## Environment Setup

To set up the environment, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Yoppman/fiton-Bot.git
   cd fiton-Bot
   ```

2. **Install dependencies** using [Poetry](https://python-poetry.org/):
   ```bash
   poetry install
   ```

3. **Set up environment variables**:
   - Create a `.env` file based on the provided `.env.template`.
   - Add your Telegram Bot Token and OpenAI API Key in the `.env` file.

4. **Run the bot**:
   Use the following command to run the bot:
   ```bash
   make run
   ```

5. **Interact with the bot**:
   - Send the `/start` command to initiate the bot.
   - Upload photos or ask questions to get professional feedback and health advice.

## Project Structure

```
├── fitonbot/
│   ├── __init__.py
│   ├── bot.py        # Main bot logic and handlers
│   ├── ai_client.py  # Logic for OpenAI API integration
│   └── photo_handler.py  # Logic for handling user-uploaded photos
├── tests/
│   ├── test_bot.py   # Unit tests for bot commands
│   └── test_ai.py    # Unit tests for AI client
├── utils/
│   ├── helpers.py    # Utility functions
├── .env.template     # Template for environment variables
├── poetry.lock       # Poetry lock file
├── pyproject.toml    # Poetry project file
├── README.md         # Project README
└── requirements.txt  # Dependency file for non-poetry setups
```

## Contributing

If you'd like to contribute to this project, please fork the repository and submit a pull request. Ensure that you write tests for any new functionality and that all tests pass before submitting your PR.

---

Start interacting with the bot [here](https://t.me/Fit_ioBot).
