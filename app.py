import asyncio
import random
import os
import logging
from telegram import Update, Message
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- Налаштування ---
# Отримуємо токен зі змінних середовища Render
BOT_TOKEN = os.environ.get('BOT_TOKEN')
# Вкажіть username вашого каналу (з @ або без, бот сам підлаштується)
TARGET_CHANNEL = '@t1246fdf' 
REACTIONS_LIST = ['❤️', '🔥', '👍', '❤️‍🔥'] # Ваші реакції
MIN_DELAY = 20  # 2 хвилини
MAX_DELAY = 30  # 5 хвилин
# -------------------

# --- Налаштування логування ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
# -----------------------------

async def handle_new_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник нових повідомлень у каналі."""
    # Отримуємо пост з каналу
    channel_post: Message = update.channel_post
    if not channel_post:
        # Якщо це не повідомлення каналу, ігноруємо
        return

    # Перевіряємо, чи повідомлення з нашого цільового каналу
    # Це робить код стійкішим до різних форматів ID та username
    channel_id = channel_post.chat_id
    channel_username = channel_post.chat.username
    target_cleaned = TARGET_CHANNEL.lstrip('@')
    if channel_username != target_cleaned and str(channel_id) != target_cleaned:
        # Якщо ID або username не співпадають, ігноруємо
        logger.info(f"Отримано пост з каналу {channel_username or channel_id}, але очікується {TARGET_CHANNEL}. Ігноруємо.")
        return

    logger.info(f"✅ Виявлено новий пост! Channel: {channel_post.chat.title or TARGET_CHANNEL}, ID: {channel_post.message_id}")

    # Генеруємо випадкову затримку
    delay = random.randint(MIN_DELAY, MAX_DELAY)
    logger.info(f"⏳ Зачекаємо {delay} секунд перед реакцією...")
    await asyncio.sleep(delay)

    # Обираємо випадкову реакцію
    chosen_reaction = random.choice(REACTIONS_LIST)
    logger.info(f"❤️ Обрано реакцію: {chosen_reaction}")

    try:
        # Ставимо реакцію на пост
        await context.bot.set_message_reaction(
            chat_id=channel_post.chat_id,
            message_id=channel_post.message_id,
            reaction=[chosen_reaction]
        )
        logger.info(f"🎉 Успіх! Реакцію {chosen_reaction} поставлено на пост {channel_post.message_id}!")
    except Exception as e:
        logger.error(f"❌ ПОМИЛКА: Не вдалося поставити реакцію на пост {channel_post.message_id}. Деталі: {e}")

def main():
    """Головна функція для запуску бота."""
    # Перевіряємо, чи задано токен
    if not BOT_TOKEN:
        logger.error("❌ КРИТИЧНА ПОМИЛКА: Змінна середовища BOT_TOKEN не знайдена!")
        return

    # Створюємо застосунок
    application = Application.builder().token(BOT_TOKEN).build()

    # Додаємо обробник для канальних постів
    # filters.ChatType.CHANNEL - обробляє тільки повідомлення в каналах
    application.add_handler(MessageHandler(filters.ChatType.CHANNEL, handle_new_post))

    logger.info("🤖 Бот запускається в режимі WEBHOOK...")

    # Отримуємо порт із змінних середовища Render
    port = int(os.environ.get('PORT', 8443))
    # Отримуємо URL застосунку для вебхука
    # Render надає його автоматично, ми будуємо його вручну
    app_url = os.environ.get('RENDER_EXTERNAL_URL')
    if not app_url:
        logger.error("❌ КРИТИЧНА ПОМИЛКА: Змінна середовища RENDER_EXTERNAL_URL не знайдена. Вебхук не буде налаштовано.")
        return

    webhook_url = f"{app_url}/webhook"
    logger.info(f"🌐 Налаштовую вебхук на URL: {webhook_url}")

    # Запускаємо бота з вебхуком
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="webhook", # Шлях, який буде додано до URL
        webhook_url=webhook_url
    )

if __name__ == "__main__":
    main()