# This is a sample Python script.

# !/usr/bin/env python3
"""
Telegram qBittorrent Bot
Handles magnet links with start/stop/help commands
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from qbittorrentapi import Client
import asyncio
import re

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration - CHANGE THESE
BOT_TOKEN = "Bot token"
QB_HOST = '192.168.0.....'
QB_PORT = 8080
QB_USERNAME = 'admin'
QB_PASSWORD = 'password'

# Initialize qBittorrent client
QB = Client(
    host=QB_HOST,
    port=QB_PORT,
    username=QB_USERNAME,
    password=QB_PASSWORD
)


def is_magnet_link(text: str) -> bool:
    """Check if text is a valid magnet link"""
    return bool(re.match(r'magnet:\?xt=urn:btih:', text, re.IGNORECASE))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_text = (
        "🚀 qBittorrent Telegram Bot\n\n"
        "Send me a magnet link to add torrent!\n"
        "Commands:\n"
        "/start - Show this message\n"
        "/help - Help\n"
        "/list - List all torrents\n"
        "/stopall - Pause all torrents\n"
        "/startall - Start all torrents"
    )
    await update.message.reply_text(welcome_text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "📋 Commands:\n"
        "• /start - Welcome message\n"
        "• /help - This help\n"
        "• /list - Show all torrents\n"
        "• /stopall - Pause all torrents\n"
        "• /startall - Start all torrents\n\n"
        "💡 Just send magnet links to add torrents!"
    )
    await update.message.reply_text(help_text)


async def list_torrents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /list command"""
    try:
        torrents = QB.torrents_info()
        if not torrents:
            await update.message.reply_text("No torrents found.")
            return

        message = "📋 Active Torrents:\n\n"
        for torrent in torrents[:10]:  # Limit to 10
            state = torrent.state
            state_emoji = {
                'downloading': '⬇️',
                'pausedDL': '⏸️',
                'stalledDL': '⏳',
                'checkingDL': '🔍',
                'pausedUP': '⏸️',
                'stalledUP': '⏳',
                'checkingUP': '🔍',
                'checkingResumeData': '🔍',
                'error': '❌',
                'queuedDL': '⏳',
                'queuedUP': '⏳'
            }.get(state, '❓')

            message += (
                f"{state_emoji} <b>{torrent.name[:50]}</b>\n"
                f"Progress: {torrent.progress * 100:.1f}%\n"
                f"Size: {torrent.size / 1024 ** 3:.1f} GB\n"
                f"Hash: <code>{torrent.hash[:8]}...</code>\n\n"
            )

        await update.message.reply_text(message, parse_mode='HTML')
    except Exception as e:
        await update.message.reply_text(f"Error listing torrents: {str(e)}")


async def stop_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stopall command"""
    try:
        QB.torrents_pause(torrent_hashes='all')
        await update.message.reply_text("⏸️ All torrents paused!")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


async def start_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /startall command"""
    try:
        QB.torrents_resume(torrent_hashes='all')
        await update.message.reply_text("▶️ All torrents started!")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


async def handle_magnet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle magnet link messages"""
    text = update.message.text.strip()

    if not is_magnet_link(text):
        await update.message.reply_text("❌ Please send a valid magnet link!")
        return

    try:
        # Add torrent
        QB.torrents_add(urls=text)  # add magnet
        torrents = QB.torrents_info(sort='added_on', reverse=True)
        torrent_info = torrents[0]
        hash_ = torrent_info.hash

        torrent_info = QB.torrents_info(torrent_hashes=hash_)[0]

        # Create inline keyboard
        keyboard = [
            [InlineKeyboardButton("▶️ Start", callback_data=f"start_{hash_}")],
            [InlineKeyboardButton("⏸️ Pause", callback_data=f"stop_{hash_}")],
            [InlineKeyboardButton("ℹ️ Info", callback_data=f"info_{hash_}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message = (
            f"✅ Torrent added successfully!\n\n"
            f"📄 <b>Name:</b> {torrent_info.name[:60]}\n"
            f"🔗 <b>Hash:</b> <code>{hash_}</code>\n"
            f"📦 <b>Size:</b> {torrent_info.size / 1024 ** 3:.1f} GB"
        )

        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='HTML')

    except Exception as e:
        logger.error(f"Error adding torrent: {e}")
        await update.message.reply_text(f"❌ Failed to add torrent: {str(e)}")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline keyboard callbacks"""
    query = update.callback_query
    await query.answer()

    action, tid = query.data.split('_', 1)

    try:
        if action == 'start':
            QB.torrents_resume(torrent_hashes=tid)
            await query.edit_message_text(
                query.message.text + f"\n\n✅ Torrent <code>{tid[-6:]}</code> started!",
                parse_mode='HTML'
            )
        elif action == 'stop':
            QB.torrents_pause(torrent_hashes=tid)
            await query.edit_message_text(
                query.message.text + f"\n\n⏸️ Torrent <code>{tid[-6:]}</code> paused!",
                parse_mode='HTML'
            )
        elif action == 'info':
            torrent = QB.torrents_info(torrent_hashes=tid)[0]
            info_text = (
                f"ℹ️ Torrent Info:\n\n"
                f"📄 Name: {torrent.name[:50]}\n"
                f"📊 Progress: {torrent.progress * 100:.1f}%\n"
                f"📦 Size: {torrent.size / 1024 ** 3:.1f} GB\n"
                f"⬇️ Downloaded: {torrent.downloaded / 1024 ** 3:.1f} GB\n"
                f"📡 Speed: {torrent.dlspeed / 1024 ** 2:.1f} KB/s\n"
                f"Status: {torrent.state}"
            )
            await query.edit_message_text(info_text)

    except Exception as e:
        await query.edit_message_text(f"❌ Error: {str(e)}")


def main():
    """Start the bot"""
    # Test qBittorrent connection
    try:
        QB.sync_maindata()
        logger.info("Connected to qBittorrent successfully")
    except Exception as e:
        logger.error(f"Failed to connect to qBittorrent: {e}")
        return

    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", list_torrents))
    application.add_handler(CommandHandler("stopall", stop_all))
    application.add_handler(CommandHandler("startall", start_all))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_magnet))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Start bot
    logger.info("Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
