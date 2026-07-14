import logging
import json
import os
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"welcome_message": "Welcome to our group! 👋", "groups": []}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot is online and ready!")

async def set_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin command: /setwelcome New welcome message here"""
    if not context.args:
        await update.message.reply_text("Usage: /setwelcome <message>")
        return
    
    config = load_config()
    config["welcome_message"] = " ".join(context.args)
    save_config(config)
    
    await update.message.reply_text(f"✅ Welcome message updated:\n{config['welcome_message']}")

async def get_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check current welcome message: /getwelcome"""
    config = load_config()
    await update.message.reply_text(f"Current message:\n{config['welcome_message']}")

async def track_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Auto-track groups"""
    if update.message.chat.type in ['group', 'supergroup']:
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
    
    # Track all messages
    application.add_handler(MessageHandler(filters.ALL, track_group))
    
    logger.info("Bot started!")
    application.run_polling()

if __name__ == '__main__':
    main()
