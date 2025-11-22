# ---------- FILE: database.py ----------
import psycopg2
from psycopg2.extras import RealDictCursor
from config import DATABASE_URL

class Database:
    def __init__(self, dsn=DATABASE_URL):
        self.dsn = dsn
        self.conn = psycopg2.connect(self.dsn)
        self.conn.autocommit = True
        self._ensure_schema()

    def _ensure_schema(self):
        q = '''
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            is_premium BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT now()
        );
        CREATE TABLE IF NOT EXISTS downloads (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES users(user_id),
            url TEXT,
            platform TEXT,
            quality TEXT,
            file_path TEXT,
            created_at TIMESTAMP DEFAULT now()
        );
        CREATE TABLE IF NOT EXISTS broadcasts (
            id BIGSERIAL PRIMARY KEY,
            admin_id BIGINT,
            caption TEXT,
            button_text TEXT,
            button_url TEXT,
            photo_file_id TEXT,
            created_at TIMESTAMP DEFAULT now()
        );
        '''
        with self.conn.cursor() as cur:
            cur.execute(q)

    def add_user_if_missing(self, user_id):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO users (user_id) VALUES (%s) ON CONFLICT DO NOTHING", (user_id,))

    def set_premium(self, user_id, is_premium=True):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO users (user_id, is_premium) VALUES (%s,%s) ON CONFLICT (user_id) DO UPDATE SET is_premium = %s", (user_id, is_premium, is_premium))

    def is_premium(self, user_id):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT is_premium FROM users WHERE user_id = %s", (user_id,))
            r = cur.fetchone()
            return bool(r and r['is_premium'])

    def log_download(self, user_id, url, platform, quality, file_path):
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO downloads (user_id, url, platform, quality, file_path) VALUES (%s,%s,%s,%s,%s)", (user_id, url, platform, quality, file_path))

    def downloads_today(self, user_id):
        with self.conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM downloads WHERE user_id=%s AND created_at >= date_trunc('day', now())", (user_id,))
            return cur.fetchone()[0]

    def list_users(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT user_id FROM users")
            return [r[0] for r in cur.fetchall()]
