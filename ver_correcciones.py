import sqlite3

conn = sqlite3.connect('stats.db')
cur = conn.cursor()
for row in cur.execute('SELECT * FROM correcciones ORDER BY fecha DESC'):
    print(row)
conn.close()