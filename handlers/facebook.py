# ---------- FILE: handlers/facebook.py ----------
import os
import time
import subprocess
from utils.downloader import download_media
from utils.logger import logger
from config import PROMO_TEXT, PROMO_URL
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def is_ffmpeg_installed():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except:
        return False


def convert_to_mp4(input_path):
    """Convert .webm, .mkv, .mov → .mp4"""
    if input_path.lower().endswith(".mp4"):
        return input_path

    output_path = input_path.rsplit(".", 1)[0] + ".mp4"

    cmd = [
        "ffmpeg", "-i", input_path,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-preset", "fast",
        "-y",
        output_path
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path


def handle_facebook(update, context, quality="720"):
    url = update.message.text.strip()

    # ------- LOADING MESSAGE -------
    msg = update.message.reply_text("⏳ Memulai download Facebook...")

    # ------- LOADING BAR ANIMATION -------
    bar_len = 10
    emojis = ["⏳", "⌛"]

    for i in range(bar_len + 1):
        for em in emojis:
            filled = "■" * i
            empty = "□" * (bar_len - i)
            text = f"{em} Downloading Facebook [{filled}{empty}]"

            try:
                context.bot.edit_message_text(
                    chat_id=msg.chat_id,
                    message_id=msg.message_id,
                    text=text
                )
            except:
                pass

            time.sleep(0.25)

    try:
        # ------- DOWNLOAD MEDIA -------
        media = download_media(url, quality=quality)

        # ------- AUTO CONVERT -------
        media = convert_to_mp4(media)

        # ------- SIZE CHECK (45MB limit) -------
        if os.path.getsize(media) > 200 * 1024 * 1024:
            update.message.reply_text("❌ File lebih dari 45MB, tidak bisa dikirim lewat bot.")
            os.remove(media)
            return

        # ------- DELETE LOADING -------
        try:
            context.bot.delete_message(
                chat_id=msg.chat_id,
                message_id=msg.message_id
            )
        except:
            pass

        # ------- PROMO BUTTON -------
        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton(PROMO_TEXT, url=PROMO_URL)]]
        )

        # ------- SEND VIDEO -------
        try:
            with open(media, "rb") as vid:
                update.message.reply_video(
                    video=vid,
                    caption=f"📘 *Facebook Video {quality}p Berhasil!*",
                    parse_mode="Markdown",
                    reply_markup=buttons,
                    timeout=200
                )
        except Exception:
            logger.exception("upload error")
            update.message.reply_text("❌ Upload gagal! Internet lambat atau file terlalu besar.")
            return

        os.remove(media)

    except Exception as e:
        logger.exception("fb download error")

        # Bila gagal, edit pesan loading atau kirim pesan biasa
        try:
            context.bot.edit_message_text(
                chat_id=msg.chat_id,
                message_id=msg.message_id,
                text=f"❌ Gagal download Facebook: {str(e)}"
            )
        except:
            update.message.reply_text(f"❌ Error: {str(e)}")
