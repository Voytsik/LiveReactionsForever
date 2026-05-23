import random
import os
import logging
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

# ================= НАЛАШТУВАННЯ =================
BOT_TOKEN = os.environ.get('BOT_TOKEN')
TARGET_CHANNEL = '@t1246fdf' 
REACTIONS_LIST = ['❤️', '🔥', '👍', '❤️‍🔥'] # Ваші реакції
MIN_DELAY = 20  # 2 хвилини
MAX_DELAY = 30  # 5 хвилин
# ================================================

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---- Flask сервер для health check (Render вимагає HTTP) ----
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Бот працює!", 200

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    flask_app.run(host='0.0.0.0', port=port)

# ---- Основний бот (синхронний, без asyncio) ----
def handle_new_post(update: Update, context: CallbackContext):
    channel_post = update.channel_post
    if not channel_post:
        return

    # Перевіряємо, чи це наш канал
    channel_username = channel_post.chat.username
    target_cleaned = TARGET_CHANNEL.lstrip('@')
    if channel_username != target_cleaned:
        logger.info(f"Ігноруємо пост з каналу {channel_username}")
        return

    logger.info(f"✅ Новий пост! ID: {channel_post.message_id}")

    # Затримка (використовуємо time.sleep, бо це синхронний код)
    delay = random.randint(MIN_DELAY, MAX_DELAY)
    logger.info(f"⏳ Зачекаємо {delay} секунд...")
    import time
    time.sleep(delay)

    chosen_reaction = random.choice(REACTIONS_LIST)
    try:
        context.bot.set_message_reaction(
            chat_id=channel_post.chat_id,
            message_id=channel_post.message_id,
            reaction=[chosen_reaction]
        )
        logger.info(f"🎉 Реакцію {chosen_reaction} поставлено!")
    except Exception as e:
        logger.error(f"❌ Помилка: {e}")

def start_bot():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.chat_type.channel, handle_new_post))
    updater.start_polling()
    logger.info("🤖 Бот запущено в режимі POLLING (синхронний). Очікуємо...")
    updater.idle()  # тримає бота активним

if __name__ == "__main__":
    # Запускаємо Flask у фоновому потоці
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("✅ Flask сервер запущено")

    # Запускаємо бота в головному потоці
    start_bot()