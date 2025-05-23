import os
import sqlite3

db_path = os.environ.get("DB_PATH", "stats.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()
for row in cur.execute('SELECT * FROM correcciones ORDER BY fecha DESC'):
    print(row)
conn.close()