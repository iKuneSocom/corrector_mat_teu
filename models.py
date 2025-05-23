import os
import sqlite3

def get_db():
    db_path = os.environ.get("DB_PATH", "/data/stats.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS visitas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS correcciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula TEXT,
            ip TEXT,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()