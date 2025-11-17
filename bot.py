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
    await update.message.reply_text("Send me text. I will detect 'Referral Alert', split posts, add emojis, and bold them.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_text = update.message.text
    
    # 1. Normalize the input. 
    # If the user sends "🚨 Referral Alert 🚨", we turn it into "Referral Alert" so we can split easily.
    # If the user sends just "Referral Alert", it stays the same.
    clean_text = raw_text.replace("🚨 Referral Alert 🚨", "Referral Alert")
    
    # 2. Define the trigger phrase
    trigger = "Referral Alert"

    if trigger in clean_text:
        # Split by the phrase "Referral Alert"
        parts = clean_text.split(trigger)

        for part in parts:
            content = part.strip()
            
            # Only process if there is actual content (skip empty splits)
            if content:
                # 3. Reconstruct the message
                # We ADD the emojis back manually
                # We ADD \n\n to force a blank line
                final_message = f"<b>🚨 Referral Alert 🚨\n\n{content}</b>"
                
                await update.message.reply_text(final_message, parse_mode="HTML")
                
                # Short delay to be safe
                await asyncio.sleep(1)
    
    else:
        # Fallback: If no "Referral Alert" phrase is found, just bold the whole text.
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
