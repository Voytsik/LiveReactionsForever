import random
import os
import time
import logging
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

# ---------- CONFIGURATION ----------
BOT_TOKEN = os.environ.get('BOT_TOKEN')
# Replace with your channel's username (with @)
TARGET_CHANNEL = '@t1246fdf' 
REACTIONS_LIST = ['❤️', '🔥', '👍', '❤️‍🔥'] # Ваші реакції
MIN_DELAY = 20  # 2 хвилини
MAX_DELAY = 30  # 5 хвилин
# -----------------------------------

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask for Render health checks
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Bot is running!", 200

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    flask_app.run(host='0.0.0.0', port=port)

# Bot handler
def handle_new_post(update: Update, context: CallbackContext):
    channel_post = update.channel_post
    if not channel_post:
        return

    channel_username = channel_post.chat.username
    target_cleaned = TARGET_CHANNEL.lstrip('@')
    if channel_username != target_cleaned:
        logger.info(f"Ignoring post from @{channel_username}")
        return

    logger.info(f"✅ New post! ID: {channel_post.message_id}")

    delay = random.randint(MIN_DELAY, MAX_DELAY)
    logger.info(f"⏳ Waiting {delay} seconds...")
    time.sleep(delay)

    chosen_reaction = random.choice(REACTIONS_LIST)
    try:
        context.bot.set_message_reaction(
            chat_id=channel_post.chat_id,
            message_id=channel_post.message_id,
            reaction=[chosen_reaction]
        )
        logger.info(f"🎉 Reaction {chosen_reaction} set on post {channel_post.message_id}!")
    except Exception as e:
        logger.error(f"❌ Error setting reaction: {e}")

def start_bot():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.chat_type.channel, handle_new_post))
    updater.start_polling()
    logger.info("🤖 Bot started (synchronous polling). Waiting for new posts...")
    updater.idle()

if __name__ == "__main__":
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("✅ Flask health check server started.")
    start_bot()