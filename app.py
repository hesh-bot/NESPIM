import os
import threading
import logging
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ----- Config -----
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("Environment variable TELEGRAM_TOKEN is not set")

logging.basicConfig(level=logging.INFO)

# ----- Telegram Bot -----
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот работает ✅")

def run_bot():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start_cmd))
    # polling is blocking -> run it in a background thread
    application.run_polling()

# Start bot in a background thread
threading.Thread(target=run_bot, daemon=True).start()

# ----- Minimal Flask web server (Render requires an open PORT) -----
web = Flask(__name__)

@web.route("/")
def root():
    return "Bot is running", 200

@web.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    # Render requires binding to 0.0.0.0 and the provided $PORT
    web.run(host="0.0.0.0", port=port)
