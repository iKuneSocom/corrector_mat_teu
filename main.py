from flask import Flask, request, jsonify, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
import re
import os
import json
from models import init_db, get_db
from stats.stats_db import stats_bp

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

app.register_blueprint(stats_bp)

pattern = re.compile(r'^[A-Z]{4}\d{7}$')
STATS_FILE = 'stats.json'
last_corrections = []

# Inicializar stats si no existe
if not os.path.exists(STATS_FILE):
    with open(STATS_FILE, 'w') as f:
        json.dump({'visits': 0, 'users': [], 'corrections': 0}, f)

def load_stats():
    with open(STATS_FILE, 'r') as f:
        data = json.load(f)
        data['users'] = set(data.get('users', []))
        return data

def save_stats(data):
    with open(STATS_FILE, 'w') as f:
        data['users'] = list(data['users'])
        json.dump(data, f)

def corregir_matricula(matricula):
    limpia = re.sub(r'[^A-Za-z0-9]', '', matricula).upper()
    letras = ''.join(re.findall(r'[A-Z]', limpia))[:4]
    numeros = ''.join(re.findall(r'\d', limpia))[:7]
    corregida = letras + numeros
    es_valida = bool(pattern.fullmatch(corregida))
    return corregida, es_valida

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/validar', methods=['POST'])
def validar():
    data = request.json
    matricula = data.get('matricula', '')
    corregida, es_valida = corregir_matricula(matricula)
    return jsonify({
        'corregida': corregida,
        'es_valida': es_valida
    })

@app.route('/guardar', methods=['POST'])
def guardar():
    data = request.get_json()
    matricula = data.get('corregida')
    fecha = data.get('hora_local')
    ip = request.remote_addr
    db = get_db()
    print("Datos recibidos:", data)
    db.execute(
        "INSERT INTO correcciones (matricula, ip, fecha) VALUES (?, ?, ?)",
        (matricula, ip, fecha)
    )
    print("Insertando:", matricula, ip, fecha)
    db.commit()
    db.close()
    return jsonify({"status": "ok"})

@app.route('/api/stats')
def api_stats():
    stats = load_stats()
    ip_header = request.headers.get('X-Forwarded-For')
    print("X-Forwarded-For:", ip_header)
    print("remote_addr:", request.remote_addr)
    ip = ip_header.split(',')[0].strip() if ip_header else request.remote_addr
    # Siempre suma una visita, sea o no nueva IP
    stats['visits'] += 1
    if ip not in stats['users']:
        stats['users'].add(ip)
    save_stats(stats)
    return jsonify({
        'users': len(stats['users']),
        'visits': stats['visits'],
        'corrections': stats['corrections']
    })

@app.route('/guardar-correccion', methods=['POST'])
def guardar_correccion():
    stats = load_stats()
    stats['corrections'] += 1
    save_stats(stats)
    return jsonify(success=True)

@app.route('/api/historial')
def api_historial():
    db = get_db()
    correcciones = db.execute(
        'SELECT matricula, ip, fecha FROM correcciones ORDER BY fecha DESC LIMIT 9'
    ).fetchall()
    db.close()
    return jsonify([dict(c) for c in correcciones])

@app.route('/robots.txt')
def robots():
    return app.send_static_file('robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return app.send_static_file('sitemap.xml')

@app.route('/google935869f451a677c7.html')
def google_verification():
    return app.send_static_file('google935869f451a677c7.html')

# Puedes usar una tabla simple para el contador, o un archivo, o una variable global (menos recomendable en producción)
from models import get_db

@app.route('/contar_corregida', methods=['POST'])
def contar_corregida():
    db = get_db()
    db.execute('INSERT INTO corregidas (fecha) VALUES (CURRENT_TIMESTAMP)')
    db.commit()
    db.close()
    return '', 204  # Sin contenido

if __name__ == '__main__':
    app.run()
