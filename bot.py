import logging
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_FILE = "config.json"

# Your welcome details
WELCOME_MESSAGE = """🚀✨ COMING SOON! ✨🚀  
OUR NEW ONLINE CASINO  

🎁 Join our Official Telegram Channel NOW  
and receive 💎 DOUBLE Grand Opening Rewards! 💎  

🔥 Exclusive Updates  
🎉 Exclusive Promotions  
🎁 Exclusive Rewards  

⚠️ Available to Telegram Channel Members ONLY  

👇 Tap below to get started 👇"""

PHOTO_URL = "https://ibb.co/5WcNzvcv"  # imgbb link
CHANNEL_URL = "https://t.me/starlinkchannel"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Respond to /start command"""
    await update.message.reply_text("🤖 Bot is online and ready!")

async def get_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with photo and button"""
    try:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("👇 Join Our Channel 👇", url=CHANNEL_URL)]
        ])
        
        await update.message.reply_photo(
            photo=PHOTO_URL,
            caption=WELCOME_MESSAGE,
            reply_markup=keyboard
        )
        logger.info(f"Welcome message sent to {update.message.chat.id}")
    except Exception as e:
        logger.error(f"Error sending photo: {e}")
        await update.message.reply_text(WELCOME_MESSAGE + f"\n\n[Click here to join]({CHANNEL_URL})")

async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome when new members join"""
    if not update.message or not update.message.new_chat_members:
        return
    
    for member in update.message.new_chat_members:
        if not member.is_bot:
            try:
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("👇 Join Our Channel 👇", url=CHANNEL_URL)]
                ])
                
                await context.bot.send_photo(
                    chat_id=update.message.chat_id,
                    photo=PHOTO_URL,
                    caption=WELCOME_MESSAGE,
                    reply_markup=keyboard
                )
                logger.info(f"Welcome sent to new member in {update.message.chat_id}")
            except Exception as e:
                logger.error(f"Error sending welcome: {e}")

def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not set!")
    
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("getwelcome", get_welcome))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member))
    
    logger.info("Bot started successfully!")
    application.run_polling()

if __name__ == '__main__':
    main()
