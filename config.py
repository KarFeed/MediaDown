import os


BOT_TOKEN = os.getenv('BOT_TOKEN', '7737990743:AAFyA9DuDCZb8JVyQ6NzZtnovyp3vn0W5Gc')
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:12345@localhost:5432/botdb')
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '2076705260').split(',') if x.strip()]
DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR', 'downloads')
DAILY_LIMIT_NON_PREMIUM = int(os.getenv('DAILY_LIMIT_NON_PREMIUM', '5'))
CLEANUP_AFTER_SECONDS = int(os.getenv('CLEANUP_AFTER_SECONDS', str(60*60*2))) # default 2 hours
PROMO_TEXT = "Promo Spesial ⭐"
PROMO_URL = "https://yourlink.com"

