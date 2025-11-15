import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- This is the Flask web server part ---
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    """A simple route to check if the bot is alive."""
    return "I'm alive!"

def run_flask():
    """Runs the Flask app in a new thread."""
    # Render sets the PORT environment variable.
    port = int(os.environ.get('PORT', 5000))
    flask_app.run(host='0.0.0.0', port=port)
# -----------------------------------------------


# --- Your Bot's Logic ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me any text and I will return it in FULL BOLD.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_text = update.message.text

    # Make ENTIRE message bold using HTML
    bold_text = f"<b>{raw_text}</b>"

    await update.message.reply_text(bold_text, parse_mode="HTML")

def main():
    # Read token from environment variable
    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_TOKEN:
        raise RuntimeError("❌ TELEGRAM_BOT_TOKEN not set. Use environment variable.")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Add your handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # --- Start the Flask server in a separate thread ---
    print("Starting keep-alive server...")
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    # --------------------------------------------------

    # Start the bot
    print("🤖 Bold HTML Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()