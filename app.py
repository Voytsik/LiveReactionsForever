import random
import os
import logging
import time
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- Configuration --------------------------------
# Read bot token from environment variable
BOT_TOKEN = os.environ.get('BOT_TOKEN')
# !!! IMPORTANT: Replace with your channel's username (e.g., '@my_cool_channel')
TARGET_CHANNEL = '@t1246fdf' 
REACTIONS_LIST = ['❤️', '🔥', '👍', '❤️‍🔥'] # Ваші реакції
MIN_DELAY = 20  # 2 хвилини
MAX_DELAY = 30  # 5 хвилин
# ------------------------------------------------

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Flask server (required by Render for health checks) ---
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Bot is running!", 200

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    flask_app.run(host='0.0.0.0', port=port)

# --- The Main Bot Logic ---
async def handle_new_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """This function is called whenever a new post appears in a channel."""
    channel_post = update.channel_post
    if not channel_post:
        return

    # Check if the post is from our target channel
    channel_username = channel_post.chat.username
    target_cleaned = TARGET_CHANNEL.lstrip('@')
    
    # Ignore posts from other channels the bot might be in
    if channel_username != target_cleaned:
        logger.info(f"Ignoring post from @{channel_username} (watching @{target_cleaned})")
        return

    logger.info(f"✅ New post detected! ID: {channel_post.message_id}")

    # Wait for a random time between 2 and 5 minutes
    delay = random.randint(MIN_DELAY, MAX_DELAY)
    logger.info(f"⏳ Waiting for {delay} seconds before reacting...")
    await asyncio.sleep(delay)  # Don't forget to import asyncio at the top!
    
    # Choose a random reaction from our list
    chosen_reaction = random.choice(REACTIONS_LIST)
    try:
        # Set the reaction on the message
        await context.bot.set_message_reaction(
            chat_id=channel_post.chat_id,
            message_id=channel_post.message_id,
            reaction=[chosen_reaction]
        )
        logger.info(f"🎉 Successfully set reaction '{chosen_reaction}' on post {channel_post.message_id}!")
    except Exception as e:
        logger.error(f"❌ Failed to set reaction on post {channel_post.message_id}. Error: {e}")

async def run_bot():
    """Initializes and starts the bot in polling mode."""
    # Create the Application instance
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add a handler for channel posts.
    # The new correct way: using filters.ChatType.CHANNEL
    application.add_handler(MessageHandler(filters.ChatType.CHANNEL, handle_new_post))
    
    logger.info("🤖 Bot has started in POLLING mode. Waiting for new posts...")
    # Start the bot (this will run forever)
    await application.run_polling()

if __name__ == "__main__":
    # Start the Flask server in a background thread
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("✅ Flask health check server started.")

    # Run the bot.
    import asyncio
    asyncio.run(run_bot())