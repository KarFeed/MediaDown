# ---------- FILE: handlers/premium.py ----------
from database import Database
from utils.logger import logger
from config import ADMIN_IDS

db = Database()


def is_premium(user_id):
    return db.is_premium(user_id)


def promote_user(update, context):
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        update.message.reply_text('Hanya admin.')
        return
    if not context.args:
        update.message.reply_text('Gunakan: /promote <user_id>')
        return
    try:
        uid = int(context.args[0])
        db.set_premium(uid, True)
        update.message.reply_text(f'User {uid} dipromote jadi premium')
    except Exception as e:
        logger.exception('promote error')
        update.message.reply_text('Error: %s' % e)


def demote_user(update, context):
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        update.message.reply_text('Hanya admin.')
        return
    if not context.args:
        update.message.reply_text('Gunakan: /demote <user_id>')
        return
    try:
        uid = int(context.args[0])
        db.set_premium(uid, False)
        update.message.reply_text(f'User {uid} dihapus premium')
    except Exception as e:
        logger.exception('demote error')
        update.message.reply_text('Error: %s' % e)
