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
import dotenv
dotenv.load_dotenv()

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)
from utils import getPhotoResponse, getTextResponse

class State(Enum):
    PHOTO=1,
    REPLY_PHOTO=2,
    REPLY_TEXT=3,
    END=4

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# pre-starter
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["start"]]

    # Initialize user chat history if it doesn't exist
    if "chat_history" not in context.user_data:
        context.user_data["chat_history"] = []

    await update.message.reply_text(
        """FITON 智能健康管家是透過 AI 為每一位
        用戶量身訂做合適的健康計畫。

        食物評分 Food Rating
        使用照片或是文字跟 FITON 說你想吃什麼，
        FITON 就會直接告訴您這個食物的評分、熱量
        以及營養素分析內容

        飲食習慣紀錄 Dietary Habits Record
        告訴 FITON 您吃的食物後，FITON 會紀錄此
        食物的熱量及營養素，往後會根據用戶的飲食
        習慣逐步推薦可持續的健康飲食

        社群激勵 Community Motivation
        將 FITON 加入群組，並設為管理員，FITON 
        將會協助群主推動健康生活

        代幣獎勵 Token Rewards
        FITON 透過 AI 以及專業營養師的建議，得出
        一個運算健康指數的公式，根據每日健康指數
        的累積，可獲得相對應的代幣。

        健康報告及規劃 Health Reports and Plan
        點擊左下角的 Start 或是輸入 /start，即可開
        啟 FITON 儀表板。
        裡面有您的健康報告以及為您量身定做的健康
        菜單。
        """,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            input_field_placeholder="just press \"start\""
        ),
    )

    return State.PHOTO

# Handle photo input
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("photo of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(
        "Please send me a photo of the food for analysis, or send /skip if you prefer to use text.",
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
    
    # Append photo info to chat history (you can also store a textual reference)
    context.user_data["chat_history"].append({"role": "user", "content": "User sent a photo"})

    # Get response from GPT API with the image and chat history
    response_text = getPhotoResponse(context.user_data["chat_history"], base64_image)

    # Append GPT response to chat history
    context.user_data["chat_history"].append({"role": "assistant", "content": response_text})
    
    await update.message.reply_text(response_text)
    
    return State.REPLY_PHOTO

# Cancel the conversation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

# Main function to run the bot
def main() -> None:
    token = os.getenv("BOT_TOKEN")  # Load token from environment variable
    print(token)
    
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).build()

    # Add conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            State.PHOTO: [
                MessageHandler(None, photo),  # Handles photo input
            ],
            State.REPLY_PHOTO: [
                MessageHandler(filters.PHOTO, replyPhoto),  # Handles the reply to photo
                MessageHandler(filters.TEXT, replyText)  # Handles the reply to text
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()