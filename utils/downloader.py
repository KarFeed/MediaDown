# ---------- FILE: utils/downloader.py ----------
import os
import yt_dlp
from config import DOWNLOAD_DIR
from utils.logger import logger

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Format MP4-only
QUALITY_MAP = {
    "360":  "bestvideo[ext=mp4][height<=360]+bestaudio[ext=m4a]/best[ext=mp4]",
    "480":  "bestvideo[ext=mp4][height<=480]+bestaudio[ext=m4a]/best[ext=mp4]",
    "720":  "bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4]",
    "1080": "bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]",
}


def download_media(url: str, quality: str = "720") -> str:
    """
    Download media langsung dalam format MP4 (tanpa WEBM).
    """
    format_selector = QUALITY_MAP.get(quality, QUALITY_MAP["720"])

    filename = os.path.join(DOWNLOAD_DIR, "%(title)s.mp4")

    ydl_opts = {
        "outtmpl": filename,
        "format": format_selector,
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "retries": 2,
    }

    try:
        logger.info(f"[YDL] Downloading: {url} | quality={quality}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            out = ydl.prepare_filename(info).replace(".webm", ".mp4").replace(".mkv", ".mp4")

        return out

    except Exception:
        logger.exception("download failed")
        raise
