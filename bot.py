import os
import threading
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- Flask Keep-Alive Server ---
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "I'm alive!"

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    flask_app.run(host='0.0.0.0', port=port)
# -------------------------------


# --- Bot Logic ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me the bulk text. I will split them and add a blank line after the header.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_text = update.message.text
    
    # 1. Define the separator
    delimiter = "🚨 Referral Alert 🚨"

    if delimiter in raw_text:
        parts = raw_text.split(delimiter)

        for part in parts:
            clean_part = part.strip()
            if clean_part:
                # 🚨 UPDATED LINE BELOW: Added \n\n for the empty line
                final_message = f"<b>{delimiter}\n\n{clean_part}</b>"
                
                await update.message.reply_text(final_message, parse_mode="HTML")
                await asyncio.sleep(1) # Delay to prevent spam blocking
    
    else:
        # If it's just a regular message without the specific header, bold it all.
        # You can also add \n\n here if you want the header separated (if the user typed it manually)
        bold_text = f"<b>{raw_text}</b>"
        await update.message.reply_text(bold_text, parse_mode="HTML")

def main():
    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_TOKEN:
        raise RuntimeError("❌ TELEGRAM_BOT_TOKEN not set.")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Starting keep-alive server...")
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
