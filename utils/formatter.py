from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# ===========================
# FORMAT PESAN DASAR
# ===========================

def format_start_message():
    return (
        "👋 *Selamat datang!*\n\n"
        "Kirimkan link dari:\n"
        "- Instagram\n"
        "- TikTok\n"
        "- Facebook\n"
        "- YouTube\n\n"
        "Bot akan mendownload otomatis sesuai platform.\n"
        "Jika butuh *kualitas 1080p*, jadilah User Premium ⭐"
    )


def format_premium_needed():
    return (
        "⚠️ *Fitur Khusus Premium*\n\n"
        "Kualitas *1080p* hanya untuk user premium.\n"
        "Silakan upgrade terlebih dahulu."
    )

# ===========================
# BUTTON KUALITAS DOWNLOAD
# ===========================

def quality_buttons(video_id: str, is_premium: bool):
    """
    video_id = ID unik video dari yt-dlp handler
    is_premium = True/False (hasil cek database)
    """

    buttons = [
        [InlineKeyboardButton("360p", callback_data=f"q360|{video_id}")],
        [InlineKeyboardButton("480p", callback_data=f"q480|{video_id}")],
        [InlineKeyboardButton("720p", callback_data=f"q720|{video_id}")],
    ]

    # 1080p tombol tetap terlihat, tapi jika user klik dan bukan premium → tolak
    if is_premium:
        buttons.append(
            [InlineKeyboardButton("1080p ⭐", callback_data=f"q1080|{video_id}")]
        )
    else:
        buttons.append(
            [InlineKeyboardButton("1080p (Premium)", callback_data=f"q1080_locked")]
        )

    return InlineKeyboardMarkup(buttons)

# ===========================
# BUTTON LINK (untuk broadcast admin)
# ===========================

def link_button(text: str, url: str):
    """
    Membuat 1 button link: "Join Channel", "Kunjungi Website", dll.
    """
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text=text, url=url)]]
    )


# ===========================
# BUTTON MULTI-LINK
# ===========================

def multi_link_buttons(buttons_list):
    """
    buttons_list = [
       ("Join Channel", "https://t.me/test"),
       ("Website", "https://domain.com")
    ]
    """
    keyboard = [
        [InlineKeyboardButton(text, url=url)]
        for (text, url) in buttons_list
    ]

    return InlineKeyboardMarkup(keyboard)


# ===========================
# FORMAT BROADCAST
# ===========================

def format_broadcast_text(text):
    return (
        "📢 *Broadcast Admin*\n\n"
        f"{text}"
    )
