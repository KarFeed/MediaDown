# ---------- FILE: handlers/tiktok.py ----------
import os
import time
from utils.downloader import download_media
from utils.logger import logger
from config import PROMO_TEXT, PROMO_URL
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def handle_tiktok(update, context):
    url = update.message.text.strip()

    # Pesan loading awal
    msg = update.message.reply_text("⏳ Memulai download TikTok...")

    # ───────────────
    # ANIMASI LOADING BAR + EMOJI BERGANTIAN
    # ───────────────
    bar_length = 10
    bar_progress = 0

    # Emoji berulang
    emoji_cycle = ["⏳", "⌛"]

    for i in range(bar_length + 1):
        bar_progress = i
        for emoji in emoji_cycle:
            # Bangun bar
            filled = "■" * bar_progress
            empty = "□" * (bar_length - bar_progress)
            text = f"{emoji} Downloading TikTok [{filled}{empty}]"
            try:
                context.bot.edit_message_text(
                    chat_id=msg.chat_id,
                    message_id=msg.message_id,
                    text=text
                )
            except:
                pass
            time.sleep(0.3)  # kecepatan animasi

    try:
        # Download video
        media_path = download_media(url, quality='720')

        # Hapus pesan loading
        context.bot.delete_message(
            chat_id=msg.chat_id,
            message_id=msg.message_id
        )

        # Button promo
        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton(PROMO_TEXT, url=PROMO_URL)]]
        )

        # Kirim video
        with open(media_path, 'rb') as video:
            update.message.reply_video(
                video=video,
                caption="🎬 *TikTok Berhasil Didownload!*\n\nKlik tombol di bawah 👇",
                parse_mode="Markdown",
                reply_markup=buttons
            )

        # Hapus file
        if os.path.exists(media_path):
            os.remove(media_path)

    except Exception as e:
        logger.exception("tiktok download error")
        context.bot.edit_message_text(
            chat_id=msg.chat_id,
            message_id=msg.message_id,
            text=f"❌ Gagal download TikTok: {str(e)}"
        )
