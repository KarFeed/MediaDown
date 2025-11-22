# ---------- FILE: handlers/broadcast.py ----------
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ConversationHandler
from utils.logger import logger
from database import Database
from config import ADMIN_IDS

B_PHOTO, B_TEXT, B_BUTTON_TEXT, B_BUTTON_URL, B_CONFIRM = range(5)

_db = Database()


def broadcast_start(update, context):
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        update.message.reply_text('Hanya admin yang dapat melakukan broadcast.')
        return ConversationHandler.END
    update.message.reply_text('Kirim foto untuk broadcast atau /skip untuk tanpa foto')
    return B_PHOTO


def broadcast_receive_photo(update, context):
    photo = update.message.photo[-1]
    context.user_data['bcast_photo'] = photo.file_id
    update.message.reply_text('Foto diterima. Sekarang kirim teks broadcast.')
    return B_TEXT


def broadcast_skip_photo(update, context):
    context.user_data['bcast_photo'] = None
    update.message.reply_text('Tanpa foto. Sekarang kirim teks broadcast.')
    return B_TEXT


def broadcast_receive_text(update, context):
    context.user_data['bcast_text'] = update.message.text
    update.message.reply_text("Ketik teks tombol (contoh: 'Kunjungi') atau /skip_button untuk tanpa tombol")
    return B_BUTTON_TEXT


def broadcast_button_text(update, context):
    context.user_data['bcast_btn_text'] = update.message.text
    update.message.reply_text('Sekarang kirim URL tombol')
    return B_BUTTON_URL


def broadcast_skip_button(update, context):
    context.user_data['bcast_btn_text'] = None
    context.user_data['bcast_btn_url'] = None
    update.message.reply_text('Siap. Ketik /confirm untuk kirim atau /cancel untuk batal')
    return B_CONFIRM


def broadcast_button_url(update, context):
    context.user_data['bcast_btn_url'] = update.message.text
    update.message.reply_text('Siap. Ketik /confirm untuk kirim atau /cancel untuk batal')
    return B_CONFIRM


def broadcast_confirm(update, context):
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        update.message.reply_text('Hanya admin.')
        return ConversationHandler.END

    photo_file = context.user_data.get('bcast_photo')
    caption = context.user_data.get('bcast_text') or ''
    btn_text = context.user_data.get('bcast_btn_text')
    btn_url = context.user_data.get('bcast_btn_url')

    # save broadcast to DB
    _db_conn = _db
    with _db_conn.conn.cursor() as cur:
        cur.execute("INSERT INTO broadcasts (admin_id, caption, button_text, button_url, photo_file_id) VALUES (%s,%s,%s,%s,%s)", (user.id, caption, btn_text, btn_url, photo_file))

    keyboard = None
    if btn_text and btn_url:
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(btn_text, url=btn_url)]])

    users = _db_conn.list_users()
    sent = 0
    for uid in users:
        try:
            if photo_file:
                context.bot.send_photo(chat_id=uid, photo=photo_file, caption=caption, reply_markup=keyboard, parse_mode=ParseMode.HTML)
            else:
                context.bot.send_message(chat_id=uid, text=caption, reply_markup=keyboard, parse_mode=ParseMode.HTML)
            sent += 1
        except Exception:
            # ignore
            pass

    update.message.reply_text(f'Broadcast selesai. Terkirim ke ~{sent} user')
    return ConversationHandler.END


def broadcast_cancel(update, context):
    update.message.reply_text('Broadcast dibatalkan.')
    return ConversationHandler.END
