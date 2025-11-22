# ---------- FILE: handlers/youtube.py ----------
import os
import time
import subprocess
from utils.downloader import download_media
from utils.logger import logger
from config import PROMO_TEXT, PROMO_URL
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Cek ffmpeg
def is_ffmpeg_installed():
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except:
        return False


def convert_to_mp4(input_path):
    """Convert .webm / .mkv / .mov ke .mp4"""
    if input_path.lower().endswith(".mp4"):
        return input_path  # tidak perlu convert

    output_path = input_path.rsplit('.', 1)[0] + ".mp4"

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


def handle_youtube(update, context, quality="720"):
    user = update.effective_user

    # Premium
    if quality == "1080" and not _db.is_premium(user.id):
        update.message.reply_text("⭐ 1080p hanya untuk User Premium!")
        return

    # ffmpeg wajib jika 1080p
    if quality == "1080" and not is_ffmpeg_installed():
        update.message.reply_text("❌ FFmpeg tidak terinstal. 1080p tidak bisa diproses.")
        return

    # Pesan loading
    msg = update.message.reply_text("⏳ Memulai download YouTube...")

    # ───────────────
    # ANIMASI BERGERAK
    # ───────────────
    bar_len = 10
    emojis = ["⏳", "⌛"]

    for i in range(bar_len + 1):
        for em in emojis:
            filled = "■" * i
            empty = "□" * (bar_len - i)
            teks = f"{em} Downloading YouTube [{filled}{empty}]"

            try:
                context.bot.edit_message_text(
                    chat_id=msg.chat_id,
                    message_id=msg.message_id,
                    text=teks
                )
            except:
                pass
            time.sleep(0.25)

    try:
        # Download video
        url = update.message.text.strip()
        media = download_media(url, quality=quality)

        # Convert jika hasilnya webm / mkv
        media = convert_to_mp4(media)

        # Cek ukuran file sebelum kirim
        if os.path.getsize(media) > 45 * 1024 * 1024:
            update.message.reply_text("❌ File terlalu besar (>45MB) tidak bisa dikirim lewat Telegram Bot.")
            os.remove(media)
            return

        # Hapus loading bar
        try:
            context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)
        except:
            pass

        # Tombol promo
        buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton(PROMO_TEXT, url=PROMO_URL)]]
        )

        # Kirim video (timeout besar biar tidak error)
        try:
            with open(media, "rb") as vid:
                update.message.reply_video(
                    video=vid,
                    caption=f"🎬 *YouTube {quality}p Berhasil Didownload!*",
                    parse_mode="Markdown",
                    reply_markup=buttons,
                    timeout=200
                )
        except Exception as e:
            logger.exception("upload error")
            update.message.reply_text("❌ Upload gagal (koneksi lambat / file besar).")
            return

        # Auto hapus file
        os.remove(media)

    except Exception as e:
        logger.exception("yt download error")
        try:
            context.bot.edit_message_text(
                chat_id=msg.chat_id,
                message_id=msg.message_id,
                text=f"❌ Gagal download YouTube: {str(e)}"
            )
        except:
            update.message.reply_text(f"❌ Gagal download: {str(e)}")
