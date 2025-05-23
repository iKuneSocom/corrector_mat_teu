import os
import sqlite3
from flask import Flask, jsonify

app = Flask(__name__)

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
    c.execute('''
        CREATE TABLE IF NOT EXISTS corregidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/api/contadores')
def api_contadores():
    db = get_db()
    total_correcciones = db.execute('SELECT COUNT(*) FROM correcciones').fetchone()[0]
    total_corregidas = db.execute('SELECT COUNT(*) FROM corregidas').fetchone()[0]
    db.close()
    return jsonify({
        'corregidas': total_corregidas,
        'copiadas': total_correcciones
    })