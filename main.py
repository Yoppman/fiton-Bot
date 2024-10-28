#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
from enum import Enum
import logging
import os
import base64
from io import BytesIO
from PIL import Image
import requests
import asyncio
import dotenv

dotenv.load_dotenv()

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, BotCommand
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    PreCheckoutQueryHandler,
    CallbackQueryHandler
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils import getPhotoResponse, getTextResponse, escape_markdown_v2
from utils.save_food_to_db import write_food_photo_to_db
from utils.payment import pay, precheckout_callback, successful_payment_callback

class State(Enum):
    HEALTH_STATE=1,
    PHOTO=2,
    REPLY_PHOTO=3,
    REPLY_TEXT=4,
    END=5

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

API_BASE_URL = "http://127.0.0.1:8000"  # Adjust this to match your backend's base URL

# pre-starter
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["start"]]
    telegram_user_id = update.message.from_user.id  # Unique Telegram user ID
    telegram_user_name = update.message.from_user.username  # Username from Telegram
    print("name:", telegram_user_name)
    print("id:", telegram_user_id)


    # Define the endpoint and payload for the API request
    user_api_url = f"{API_BASE_URL}/users/"
    user_data = {
        "name": telegram_user_name,
        "age": 0,
        "height": 0,
        "weight": 0,
        "telegram_id": telegram_user_id,
        "goal": "default"
    }

    # Check if the user already exists by name
    response = requests.get(f"{user_api_url}?name={telegram_user_name}")

    if response.status_code == 404:
        # User not found, proceed to create
        create_response = requests.post(user_api_url, json=user_data)
        if create_response.status_code == 201:
            print("User created successfully.")
        else:
            print("Failed to create user:", create_response.json())
    elif response.status_code == 200:
        # User already exists
        print("User already exists.")
    else:
        # Handle other unexpected errors
        print("Error occurred:", response.status_code, response.json())

    # Initialize user chat history if it doesn't exist in the context
    if "chat_history" not in context.user_data:
        context.user_data["chat_history"] = []

    # Send a reply to the user
    reply_keyboard = [["Press to continue"]]

    await update.message.reply_text(
        f"🎉 Hello, ✨<b><u> {telegram_user_name.upper()} </u></b>✨  Welcome to 🌟 <b>Lipo-Out</b> 🌟 ",
        parse_mode="HTML",  # Enable Markdown for bold text
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
        ),
    )

    return State.HEALTH_STATE

# Ask the user for their health goal
async def heathState(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Inline keyboard with health goals
    keyboard = [
        [InlineKeyboardButton("🌱 Moderate", callback_data="goal_Moderate")],
        [InlineKeyboardButton("💪 Fit", callback_data="goal_Fit")],
        [InlineKeyboardButton("🏋️ Bodybuilder", callback_data="goal_Bodybuilder")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "<b>What is your health goal? Choose one to get started:</b>",
        parse_mode="HTML",
        reply_markup=reply_markup,
    )

    return State.HEALTH_STATE

# Handle the health goal choice and save it to the database
async def handle_goal_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()  # Acknowledge the button click

    # Get the selected goal from callback data
    selected_goal = query.data.split("_")[1]

    # Update user's goal in the database
    telegram_user_id = update.callback_query.from_user.id
    user_api_url = f"{API_BASE_URL}/users/?telegram_id={telegram_user_id}"
    update_data = {"goal": selected_goal}

    response = requests.patch(user_api_url, json=update_data)
    if response.status_code == 200:
        await query.edit_message_text(
            f"""Your goal is set to <b>{selected_goal}</b>! 🎯

<b>Lipo-Out</b> will help guide you step-by-step towards reaching your goal, using your body data, eating habits, and the target you’ve chosen.

Ready to get started? 📸 Upload a photo, and we’ll take care of the analysis for you!""",
            parse_mode=ParseMode.HTML
        )    
    else:   
        await query.edit_message_text("There was an issue setting your goal. Please try again.")

    # Transition to the next state, such as PHOTO
    return State.REPLY_PHOTO

# Handle photo input
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    message = update.message.text

    logger.info(
        "photo of %s: %s",
        user.first_name, update.message.text
    )

    selectedState = update.message.text
    await update.message.reply_text(
        f"""Your goal is set to <b>{selectedState.upper()}</b>! 🎯

<b>Lipo-Out</b> will help guide you step-by-step towards reaching your goal, using your body data, eating habits, and the target you’ve chosen.

Ready to get started? 📸 Upload a photo, and we’ll take care of the analysis for you!""",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )

    return State.REPLY_PHOTO

# Handle text input
async def replyText(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    user_input = update.message.text
    logger.info("Text message from %s: %s", user.first_name, user_input)

    # Append to user's chat history
    context.user_data["chat_history"].append({"role": "user", "content": user_input})

    # Get response from GPT API based on chat history
    response_text = getTextResponse(context.user_data["chat_history"])

    # Append GPT response to chat history
    context.user_data["chat_history"].append({"role": "assistant", "content": response_text})

    await update.message.reply_text(response_text)
    
    return State.REPLY_PHOTO


# Reply to photo
async def replyPhoto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()

    # Read the photo content directly into memory without saving it to disk
    photo_bytes = await photo_file.download_as_bytearray()

    # Encode the photo content to base64
    base64_image = base64.b64encode(photo_bytes).decode("utf-8")
    
    logger.info("Photo of %s: processed.", user.first_name)
    
    # Append photo info to chat history
    context.user_data["chat_history"].append({"role": "user", "content": "User sent a photo"})

    # Send a temporary "loading" message to the user
    loading_message = await update.message.reply_text("Processing your image, please wait ... ✨")

    # Get both the text response and chart from GPT API
    response = getPhotoResponse(context.user_data["chat_history"], base64_image)
    response_text = response["text_response"]
    chart_base64 = response["chart_image_base64"]
    
    # Append GPT response to chat history
    context.user_data["chat_history"].append({"role": "assistant", "content": response_text})
    
    # Edit the loading message with the final text response
    response_text_escaped = escape_markdown_v2(response_text)
    await loading_message.edit_text(response_text_escaped, parse_mode=ParseMode.MARKDOWN_V2)
    
    if chart_base64 is not None:
        # Decode the chart image from base64 and send it back as a photo
        chart_bytes = base64.b64decode(chart_base64)
        chart_image = Image.open(BytesIO(chart_bytes))

        # Convert the chart to a byte stream so it can be sent as a photo
        with BytesIO() as image_binary:
            chart_image.save(image_binary, format='PNG')
            image_binary.seek(0)
            await update.message.reply_photo(photo=image_binary)

        telegram_user_id = update.message.from_user.id  # Unique Telegram user ID

        # Ask the user if they want to save this meal to the database
        keyboard = [
            [
                InlineKeyboardButton("Yes", callback_data="save_yes"),
                InlineKeyboardButton("No", callback_data="save_no"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Would you like to save this meal to your record?", reply_markup=reply_markup)

        # Store photo and analysis details in context for callback use
        context.user_data["photo_bytes"] = photo_bytes
        context.user_data["response_text"] = response_text
        context.user_data["telegram_user_id"] = telegram_user_id

    return State.REPLY_PHOTO

# Callback handler to process the user’s choice
async def handle_save_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge the button click

    # Determine if the user selected "Yes" or "No"
    if query.data == "save_yes":
        # User chose to save the meal
        photo_bytes = context.user_data.get("photo_bytes")
        response_text = context.user_data.get("response_text")
        telegram_user_id = context.user_data.get("telegram_user_id")

        # Call the function to store the meal in the database
        write_food_photo_to_db(telegram_user_id, photo_bytes, response_text)
        
        await query.edit_message_text("Meal saved to your record! ✅")
    else:
        # User chose not to save the meal
        await query.edit_message_text("Meal was not saved to your record. ❌")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation and reset the state."""
    await update.message.reply_text(
        "Your health journey is important to us. If you’re ready to continue, just type /start to begin again anytime! 💪😊"
    )
    
    # Clear user data if necessary
    context.user_data.clear()
    
    return ConversationHandler.END

def main() -> None:
    token = os.getenv("BOT_TOKEN")  # Load token from environment variable
    
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).build()
    job_queue = application.job_queue

    # Add conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],  # Starts with /start command
        states={
            State.HEALTH_STATE: [
                MessageHandler(filters.TEXT & filters.Regex("Press to continue"), heathState),
                CallbackQueryHandler(handle_goal_selection, pattern="^goal_"),  # Handles goal selection
                CommandHandler("cancel", cancel)  # Allows cancellation in this state
            ],
            State.PHOTO: [
                MessageHandler(filters.PHOTO, photo),  # Handles photo input in PHOTO state
                CommandHandler("cancel", cancel)
            ],
            State.REPLY_PHOTO: [
                CommandHandler("cancel", cancel),
                MessageHandler(filters.PHOTO, replyPhoto),  # Handles reply to a photo
                MessageHandler(filters.TEXT, replyText)  # Handles reply to text messages
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],  # Fallbacks to cancel command
        allow_reentry=True
    )

    # Add additional handlers
    application.add_handler(CommandHandler("pay", pay))
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))
    application.add_handler(CallbackQueryHandler(handle_save_choice, pattern="^save_"))

    # Add the conversation handler to the application
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()