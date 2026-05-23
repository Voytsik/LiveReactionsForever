import asyncio
import random
import os
from threading import Thread
from flask import Flask
from telegram import Bot
from telegram.ext import Application

# ================= НАЛАШТУВАННЯ =================
BOT_TOKEN = os.environ.get('BOT_TOKEN')  # Беремо токен з оточення
TARGET_CHANNEL = '@t1246fdf'  # ID або юзернейм каналу
REACTIONS_LIST = ['❤️', '🔥', '👍', '❤️‍🔥']
MIN_DELAY = 120
MAX_DELAY = 300
# ================================================

# Flask-додаток для keep-alive
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Бот працює!"

def run_flask():
    flask_app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# Функція з логікою бота (та ж сама)
async def handle_new_post(update, context):
    channel_post = update.channel_post
    if str(channel_post.chat_id) != TARGET_CHANNEL and channel_post.chat.username != TARGET_CHANNEL.lstrip('@'):
        return
    print(f"[→] Виявлено новий пост! ID: {channel_post.message_id}.")
    delay = random.randint(MIN_DELAY, MAX_DELAY)
    print(f"[⏳] Зачекаємо {delay} секунд...")
    await asyncio.sleep(delay)
    chosen_reaction = random.choice(REACTIONS_LIST)
    try:
        await context.bot.set_message_reaction(
            chat_id=channel_post.chat_id,
            message_id=channel_post.message_id,
            reaction=[chosen_reaction]
        )
        print(f"[✓] Реакцію {chosen_reaction} поставлено!")
    except Exception as e:
        print(f"[✗] Помилка: {e}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.ChatType.CHANNEL, handle_new_post))
    print("Бот запущено!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    # Запускаємо Flask у окремому потоці
    t = Thread(target=run_flask)
    t.start()
    # Запускаємо бота
    main()