import asyncio
import random
import os
import logging
from threading import Thread
from flask import Flask
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram import Update

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

# ---- Flask сервер для health check (щоб Render не вимкнув) ----
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Бот працює!", 200

@flask_app.route('/health')
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    flask_app.run(host='0.0.0.0', port=port)

# ---- Основний бот ----
async def handle_new_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ставить реакцію на новий пост у каналі"""
    channel_post = update.channel_post
    if not channel_post:
        return

    # Перевіряємо, чи пост з нашого каналу
    channel_username = channel_post.chat.username
    target_cleaned = TARGET_CHANNEL.lstrip('@')
    if channel_username != target_cleaned:
        logger.info(f"Ігноруємо пост з каналу {channel_username} (очікуємо {target_cleaned})")
        return

    logger.info(f"✅ Виявлено новий пост! ID: {channel_post.message_id}")

    # Затримка 2-5 хвилин
    delay = random.randint(MIN_DELAY, MAX_DELAY)
    logger.info(f"⏳ Зачекаємо {delay} секунд...")
    await asyncio.sleep(delay)

    # Обираємо випадкову реакцію
    chosen_reaction = random.choice(REACTIONS_LIST)
    try:
        await context.bot.set_message_reaction(
            chat_id=channel_post.chat_id,
            message_id=channel_post.message_id,
            reaction=[chosen_reaction]
        )
        logger.info(f"🎉 Реакцію {chosen_reaction} успішно поставлено!")
    except Exception as e:
        logger.error(f"❌ Помилка при постановці реакції: {e}")

async def run_bot():
    """Запуск бота в режимі polling"""
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.ChatType.CHANNEL, handle_new_post))
    logger.info("🤖 Бот запущено в режимі POLLING. Очікуємо нові пости...")
    await application.run_polling()

def start_bot_thread():
    """Запускає асинхронний бот в окремому потоці"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_bot())
    except KeyboardInterrupt:
        logger.info("Бот зупинено")
    finally:
        loop.close()

if __name__ == "__main__":
    # Запускаємо Flask-сервер у фоні (для health check)
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("Flask сервер для health check запущено")

    # Запускаємо бота в головному потоці (або окремому - неважливо)
    # Краще в окремому, щоб Flask міг відповідати на запити
    bot_thread = Thread(target=start_bot_thread, daemon=False)
    bot_thread.start()
    bot_thread.join()  # Чекаємо завершення бота