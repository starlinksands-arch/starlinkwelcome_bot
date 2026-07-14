import logging
import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "welcome_message": "Welcome to our group! 👋",
            "welcome_photo_url": "https://imgur.com/4vxE9hZ.jpg",
            "channel_url": "https://t.me/starlinkchannel",
            "groups": []
        }

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot is online and ready!")

async def send_welcome_message(chat_id, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with photo and button"""
    config = load_config()
    
    photo_url = config.get("welcome_photo_url", "https://imgur.com/4vxE9hZ.jpg")
    message_text = config.get("welcome_message", "Welcome to our group! 👋")
    channel_url = config.get("channel_url", "https://t.me/starlinkchannel")
    
    # Create inline button
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👇 Join Our Channel 👇", url=channel_url)]
    ])
    
    try:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=photo_url,
            caption=message_text,
            reply_markup=keyboard
        )
        logger.info(f"Welcome message sent to {chat_id}")
    except Exception as e:
        logger.error(f"Error sending welcome message to {chat_id}: {e}")

async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome to new members"""
    if update.message.new_chat_members:
        for member in update.message.new_chat_members:
            if not member.is_bot:
                await send_welcome_message(update.message.chat_id, context)

async def set_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set welcome message"""
    if not context.args:
        await update.message.reply_text("Usage: /setwelcome <message>")
        return
    
    config = load_config()
    config["welcome_message"] = " ".join(context.args)
    save_config(config)
    
    await update.message.reply_text(f"✅ Welcome message updated!")

async def get_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get current welcome message"""
    config = load_config()
    message_text = config.get("welcome_message", "Welcome to our group! 👋")
    photo_url = config.get("welcome_photo_url", "https://imgur.com/4vxE9hZ.jpg")
    channel_url = config.get("channel_url", "https://t.me/starlinkchannel")
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👇 Join Our Channel 👇", url=channel_url)]
    ])
    
    await update.message.reply_photo(
        photo=photo_url,
        caption=message_text,
        reply_markup=keyboard
    )

async def track_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auto-track groups"""
    if update.message and update.message.chat.type in ['group', 'supergroup']:
        config = load_config()
        group_id = update.message.chat.id
        
        if group_id not in config.get("groups", []):
            config["groups"].append(group_id)
            save_config(config)
            logger.info(f"Bot added to group {group_id}")

def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not set!")
    
    application = Application.builder().token(TOKEN).build()
    
    # Commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("setwelcome", set_welcome))
    application.add_handler(CommandHandler("getwelcome", get_welcome))
    
    # New member handler
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member))
    
    # Track all messages
    application.add_handler(MessageHandler(filters.ALL, track_group))
    
    logger.info("Bot started!")
    application.run_polling()

if __name__ == '__main__':
    main()
