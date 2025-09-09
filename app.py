# app.py
# Telegram anonymous complaints bot (aiogram v3) + Flask (Render friendly)
import os
import asyncio
import threading
from flask import Flask
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

# ---------- Конфигурация (из переменных окружения) ----------
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN не задан. Установите в Render Environment.")

ADMIN_CHAT = os.environ.get("ADMIN_CHAT_ID")
if not ADMIN_CHAT:
    raise RuntimeError("ADMIN_CHAT_ID не задан. Установите в Render Environment.")
ADMIN_CHAT_ID = int(ADMIN_CHAT)  # пример: -1001234567890 для канала/чата

# ---------- Инициализация aiogram ----------
bot = Bot(token=TOKEN)
dp = Dispatcher()

# ---------- Хендлеры (перенеси сюда свою логику) ----------
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Максимально подробно опишите проблему. Чем больше информации - тем быстрее "
        "отработают соответствующие органы! Отправьте жалобу, и я полностью передам её "
        "анонимно администраторам. Можно оставить контакты для связи."
    )

@dp.message()
async def complaint(message: Message):
    text = message.text or "<нет текста>"
    # пересылаем админам: только текст, без раскрытия пользователя
    try:
        await bot.send_message(ADMIN_CHAT_ID, f"⚠️ Новая анонимная жалоба:\n\n{text}")
        await message.answer("✅ Жалоба отправлена!")
    except Exception as e:
        # логирование (в Render видно в логах)
        print("Ошибка при отправке в админ-чат:", e)
        await message.answer("❗️ Не удалось отправить жалобу — попробуйте позже.")

# ---------- Функция запуска polling (async) ----------
async def run_bot():
    # Запускаем polling (он блокирует текущий asyncio loop)
    await dp.start_polling(bot)

# ---------- Небольшой HTTP-сервер для Render (чтобы был открыт порт) ----------
def run_http():
    app = Flask(__name__)

    @app.route("/")
    def root():
        return "Bot is running", 200

    @app.route("/health")
    def health():
        return "OK", 200

    port = int(os.environ.get("PORT", "5000"))
    # Render требует 0.0.0.0 и порт из $PORT
    app.run(host="0.0.0.0", port=port)

# ---------- Точка входа ----------
if name == "__main__":
    # Запускаем Flask в отдельном потоке — чтобы binding порта происходил в процессе
    threading.Thread(target=run_http, daemon=True).start()

    # Запускаем aiogram polling в основном потоке (asyncio)
    asyncio.run(run_bot())
