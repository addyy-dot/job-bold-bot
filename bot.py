import os
import threading
import asyncio  # Added for sleep delay
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
    await update.message.reply_text("Send me the bulk text. I will split them by 'Referral Alert' and make them BOLD.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_text = update.message.text
    
    # 1. Define the text that separates the posts.
    # We assume every post starts with this exact header.
    delimiter = "🚨 Referral Alert 🚨"

    # 2. Check if the text actually contains multiple posts
    if delimiter in raw_text:
        # Split the text by the delimiter. 
        # This creates a list, but removes the delimiter itself.
        parts = raw_text.split(delimiter)

        for part in parts:
            clean_part = part.strip()
            
            # Only process if there is text left (split sometimes creates empty strings)
            if clean_part:
                # 3. Reconstruct the message: Add the delimiter back + the content + Bold Tags
                final_message = f"<b>{delimiter}\n{clean_part}</b>"
                
                await update.message.reply_text(final_message, parse_mode="HTML")
                
                # 4. Wait 1 second between sends to avoid Telegram 'Flood Control' errors
                await asyncio.sleep(1)
    
    else:
        # If no delimiter is found, just bold the whole thing as one message
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
    print("🤖 Bold Splitter Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
