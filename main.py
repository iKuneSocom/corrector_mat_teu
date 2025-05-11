from flask import Flask, request, jsonify, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
import re
import os
import json

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

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
    data = request.json
    corregida = data.get('corregida')
    hora_local = data.get('hora_local')
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()

    if not corregida or not hora_local:
        return jsonify({'error': 'Datos incompletos'}), 400

    global last_corrections
    last_corrections.insert(0, {
        'corregida': corregida,
        'ip': ip,
        'hora_local': hora_local
    })
    last_corrections[:] = last_corrections[:9]

    # Actualiza estadísticas
    stats = load_stats()
    if ip not in stats['users']:
        stats['users'].add(ip)
        stats['visits'] += 1
    stats['corrections'] += 1
    save_stats(stats)

    return jsonify({
        'last_corrections': last_corrections,
        'ip_cliente': ip
    })

@app.route('/api/stats')
def api_stats():
    stats = load_stats()
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    if ip not in stats['users']:
        stats['users'].add(ip)
        stats['visits'] += 1
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

if __name__ == '__main__':
    app.run()
