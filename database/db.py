import sqlite3
import os
from typing import Optional, List, Tuple, Any

class Database:
    def __init__(self, db_name: str = None):
        self.db_name = db_name or os.getenv('DATABASE_PATH', 'data/wishlist.db')
        # Создаем директорию для базы данных, если её нет
        os.makedirs(os.path.dirname(self.db_name), exist_ok=True)

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        return self.conn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()
        self.conn.close()

    def init_db(self):
        with self as cursor:
            cursor.execute('''CREATE TABLE IF NOT EXISTS users
                            (user_id INTEGER PRIMARY KEY,
                             username TEXT,
                             notifications INTEGER DEFAULT 1)''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS wishes
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             user_id INTEGER,
                             title TEXT,
                             price REAL,
                             link TEXT,
                             photo_id TEXT,
                             date_added TIMESTAMP,
                             status TEXT DEFAULT 'active',
                             booked_by INTEGER,
                             FOREIGN KEY (user_id) REFERENCES users(user_id),
                             FOREIGN KEY (booked_by) REFERENCES users(user_id))''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS subscriptions
                            (subscriber_id INTEGER,
                             target_user_id INTEGER,
                             FOREIGN KEY (subscriber_id) REFERENCES users(user_id),
                             FOREIGN KEY (target_user_id) REFERENCES users(user_id))''')
