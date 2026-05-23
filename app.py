import asyncio
import random
import os
import logging
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# ================= НАЛАШТУВАННЯ =================
BOT_TOKEN = os.environ.get('BOT_TOKEN')
TARGET_CHANNEL = '@t1246fdf' 
REACTIONS_LIST = ['❤️', '🔥', '👍', '❤️‍🔥'] # Ваші реакції
MIN_DELAY = 120
MAX_DELAY = 300
# ================================================

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask-додаток для keep-alive (щоб Render не вимкнув сервіс)
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Бот працює!"

@flask_app.route('/health')
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    flask_app.run(host='0.0.0.0', port=port)

# Обробник нових постів
async def handle_new_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel_post = update.channel_post
    if not channel_post:
        return

    # Перевіряємо, чи це наш канал
    channel_username = channel_post.chat.username
    target_cleaned = TARGET_CHANNEL.lstrip('@')
    if channel_username != target_cleaned:
        logger.info(f"Отримано пост з каналу {channel_username}, ігноруємо")
        return

    logger.info(f"✅ Новий пост! ID: {channel_post.message_id}")

    delay = random.randint(MIN_DELAY, MAX_DELAY)
    logger.info(f"⏳ Зачекаємо {delay} секунд...")
    await asyncio.sleep(delay)

    chosen_reaction = random.choice(REACTIONS_LIST)
    try:
        await context.bot.set_message_reaction(
            chat_id=channel_post.chat_id,
            message_id=channel_post.message_id,
            reaction=[chosen_reaction]
        )
        logger.info(f"🎉 Реакцію {chosen_reaction} поставлено!")
    except Exception as e:
        logger.error(f"❌ Помилка: {e}")

async def main():
    # Створюємо Application
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.ChatType.CHANNEL, handle_new_post))

    # Отримуємо URL для вебхука
    app_url = os.environ.get('RENDER_EXTERNAL_URL')
    if not app_url:
        logger.error("❌ RENDER_EXTERNAL_URL не задано!")
        return
    webhook_url = f"{app_url}/webhook"
    port = int(os.environ.get('PORT', 8443))

    logger.info(f"🤖 Запуск вебхука на {webhook_url}")

    # Запускаємо вебхук (цей метод блокує виконання)
    await application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="webhook",
        webhook_url=webhook_url,
        secret_token=None,  # можна додати для безпеки
    )

if __name__ == "__main__":
    # Запускаємо Flask у окремому потоці для keep-alive
    t = Thread(target=run_flask, daemon=True)
    t.start()

    # Запускаємо бота через asyncio.run()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот зупинено")