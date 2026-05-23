import os
import random
import time
import logging
import threading
import requests
from flask import Flask

# ---------- CONFIGURATION ----------
BOT_TOKEN = os.environ.get('BOT_TOKEN')
# Your channel username (with @, e.g., '@my_channel')
TARGET_CHANNEL = '@t1246fdf' 
REACTIONS_LIST = ['❤️', '🔥', '👍', '❤️‍🔥'] # Ваші реакції
MIN_DELAY = 20  # 2 хвилини
MAX_DELAY = 30  # 5 хвилин
# -----------------------------------

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---- Flask for Render health checks ----
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Bot is running!", 200

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    flask_app.run(host='0.0.0.0', port=port)

# ---- Core bot logic using raw Telegram Bot API ----
def get_updates(offset=None):
    """Fetch new updates from Telegram."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {'timeout': 30, 'allowed_updates': ['channel_post']}
    if offset:
        params['offset'] = offset
    try:
        resp = requests.get(url, params=params, timeout=35)
        return resp.json().get('result', [])
    except Exception as e:
        logger.error(f"Error getting updates: {e}")
        return []

def set_reaction(chat_id, message_id, reaction):
    """Set a reaction on a message."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMessageReaction"
    payload = {
        'chat_id': chat_id,
        'message_id': message_id,
        'reaction': [{'type': 'emoji', 'emoji': reaction}]
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.ok
    except Exception as e:
        logger.error(f"Error setting reaction: {e}")
        return False

def process_updates():
    """Main loop: poll for new channel posts and react."""
    last_update_id = None
    logger.info("🤖 Bot started (polling with requests). Waiting for new posts...")
    
    while True:
        updates = get_updates(offset=last_update_id)
        for upd in updates:
            update_id = upd['update_id']
            last_update_id = update_id + 1  # mark as processed
            
            channel_post = upd.get('channel_post')
            if not channel_post:
                continue
            
            chat = channel_post.get('chat', {})
            chat_username = chat.get('username')
            if chat_username != TARGET_CHANNEL.lstrip('@'):
                continue
            
            message_id = channel_post.get('message_id')
            logger.info(f"✅ New post in {chat_username} (ID: {message_id})")
            
            # Random delay
            delay = random.randint(MIN_DELAY, MAX_DELAY)
            logger.info(f"⏳ Waiting {delay} seconds...")
            time.sleep(delay)
            
            reaction = random.choice(REACTIONS_LIST)
            success = set_reaction(chat['id'], message_id, reaction)
            if success:
                logger.info(f"🎉 Reaction {reaction} set on post {message_id}")
            else:
                logger.error(f"❌ Failed to set reaction on post {message_id}")
        
        time.sleep(1)  # small pause to avoid busy loop

# ---- Start everything ----
if __name__ == "__main__":
    # Start Flask in a background thread (for Render)
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("✅ Flask health check server started.")
    
    # Run the bot's main loop (blocks forever)
    process_updates()