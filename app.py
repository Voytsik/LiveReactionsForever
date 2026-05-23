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

# ---- Flask сервер для health check (Render вимагає HTTP-ендпоінт) ----
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Бот працює!", 200

@flask_app.route('/health')
def health():
    return "OK", 200

def run_flask():
    """Запускає Flask-сервер у окремому потоці"""
    port = int(os.environ.get('PORT', 8080))
    flask_app.run(host='0.0.0.0', port=port)

# ---- Основний бот (ставлення реакцій) ----
async def handle_new_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    channel_post = update.channel_post
    if not channel_post:
        return

    # Перевіряємо, чи це наш канал
    channel_username = channel_post.chat.username
    target_cleaned = TARGET_CHANNEL.lstrip('@')
    if channel_username != target_cleaned:
        logger.info(f"Ігноруємо пост з каналу {channel_username} (очікуємо {target_cleaned})")
        return

    logger.info(f"✅ Виявлено новий пост! ID: {channel_post.message_id}")

    # Випадкова затримка від 2 до 5 хвилин
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
    """Запуск бота в режимі polling (у головному потоці)"""
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.ChatType.CHANNEL, handle_new_post))
    logger.info("🤖 Бот запущено в режимі POLLING. Очікуємо нові пости...")
    await application.run_polling()

if __name__ == "__main__":
    # Запускаємо Flask у фоновому потоці (він не заважає сигналам)
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    logger.info("✅ Flask сервер для health check запущено")

    # Запускаємо бота в головному потоці (щоб уникнути помилки set_wakeup_fd)
    asyncio.run(run_bot())