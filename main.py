# ---------- FILE: main.py ----------
import os
import threading
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from config import BOT_TOKEN, ADMIN_IDS, DOWNLOAD_DIR, DAILY_LIMIT_NON_PREMIUM
from utils.logger import logger
from utils.cleanup_worker import cleanup_worker
from database import Database
from handlers import instagram, facebook, tiktok, youtube, premium
from handlers.broadcast import (
    broadcast_start, broadcast_receive_photo, broadcast_skip_photo, broadcast_receive_text,
    broadcast_button_text, broadcast_skip_button, broadcast_button_url, broadcast_confirm, broadcast_cancel,
    B_PHOTO, B_TEXT, B_BUTTON_TEXT, B_BUTTON_URL, B_CONFIRM
)
from telegram.ext import ConversationHandler

# start cleanup worker
threading.Thread(target=cleanup_worker, daemon=True).start()

# init db
_db = Database()


def start(update, context):
    user = update.effective_user
    _db.add_user_if_missing(user.id)

    text = (
        "👋 *Halo, Selamat Datang di Bot Downloader!*\n\n"
        "Kirimkan link dari salah satu platform berikut, dan bot akan mendownloadnya otomatis:\n\n"
        "📸 Instagram  \n"
        "🎵 TikTok  \n"
        "📘 Facebook  \n"
        "▶️ YouTube \n\n"
        "✨ *Fitur Premium:*  \n"
        "- Download video hingga *1080p*  \n"
        "- Akses lebih cepat & tanpa batasan \n\n"
        "⭐ Untuk menikmati kualitas terbaik, jadilah User Premium sekarang!\n\n"
        "❗ *Jika ada kendala atau pertanyaan, silakan hubungi kami:*\n"
    )

    # Tombol link
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Hubungi Admin", url="https://t.me/karfeed")],
        [InlineKeyboardButton("⭐ Join Channel", url="https://t.me/YourChannel")],
        [InlineKeyboardButton("🌐 Kunjungi Website", url="https://yourwebsite.com")]
    ])

    update.message.reply_text(text, parse_mode="Markdown", reply_markup=buttons)



def route(update, context):
    text = update.message.text.strip()
    user = update.effective_user
    _db.add_user_if_missing(user.id)

    # basic platform detection
    if any(x in text.lower() for x in ('instagram.com', 'instagr.am')):
        return instagram.handle_instagram(update, context)
    if any(x in text.lower() for x in ('facebook.com', 'fb.watch')):
        return facebook.handle_facebook(update, context)
    if 'tiktok.com' in text.lower() or 'vm.tiktok.com' in text.lower():
        return tiktok.handle_tiktok(update, context)
    if 'youtube.com' in text.lower() or 'youtu.be' in text.lower():
        return youtube.handle_youtube(update, context)

    update.message.reply_text('Link tidak dikenali. Pastikan Anda mengirim URL dari platform yang didukung.')


def promote_cmd(update, context):
    return premium.promote_user(update, context)


def demote_cmd(update, context):
    return premium.demote_user(update, context)


if __name__ == '__main__':
    if BOT_TOKEN == 'YOUR_BOT_TOKEN':
        logger.error('Atur BOT_TOKEN di config.py atau env var.')
        exit(1)

    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('promote', promote_cmd, pass_args=True))
    dp.add_handler(CommandHandler('demote', demote_cmd, pass_args=True))

    # Broadcast conversation
    bcast_conv = ConversationHandler(
        entry_points=[CommandHandler('broadcast', broadcast_start)],
        states={
            B_PHOTO: [MessageHandler(Filters.photo, broadcast_receive_photo), CommandHandler('skip', broadcast_skip_photo)],
            B_TEXT: [MessageHandler(Filters.text & ~Filters.command, broadcast_receive_text)],
            B_BUTTON_TEXT: [MessageHandler(Filters.text & ~Filters.command, broadcast_button_text), CommandHandler('skip_button', broadcast_skip_button)],
            B_BUTTON_URL: [MessageHandler(Filters.text & ~Filters.command, broadcast_button_url)],
            B_CONFIRM: [CommandHandler('confirm', broadcast_confirm), CommandHandler('cancel', broadcast_cancel)]
        },
        fallbacks=[CommandHandler('cancel', broadcast_cancel)],
        allow_reentry=True
    )
    dp.add_handler(bcast_conv)

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, route))

    updater.start_polling()
    logger.info('Bot started')
    updater.idle()

