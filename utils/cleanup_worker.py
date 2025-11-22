# ---------- FILE: utils/cleanup_worker.py ----------
import time
import os
import shutil
from config import DOWNLOAD_DIR, CLEANUP_AFTER_SECONDS
from utils.logger import logger


def cleanup_worker():
    while True:
        try:
            now_ts = time.time()
            for fname in os.listdir(DOWNLOAD_DIR):
                fpath = os.path.join(DOWNLOAD_DIR, fname)
                try:
                    mtime = os.path.getmtime(fpath)
                    if now_ts - mtime > CLEANUP_AFTER_SECONDS:
                        if os.path.isdir(fpath):
                            shutil.rmtree(fpath, ignore_errors=True)
                        else:
                            os.remove(fpath)
                        logger.info('cleanup removed %s', fpath)
                except Exception:
                    pass
        except Exception:
            logger.exception('cleanup loop error')
        time.sleep(60 * 5)
