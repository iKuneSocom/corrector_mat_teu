from flask import Flask, request, jsonify, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
import re
import os
from models import init_db, get_db

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)
init_db()

pattern = re.compile(r'^[A-Z]{4}\d{7}$')

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

    # Guardar corrección en la base de datos
    db = get_db()
    db.execute('INSERT INTO correcciones (matricula, ip, fecha) VALUES (?, ?, ?)', (corregida, ip, hora_local))
    db.commit()
    db.close()

    return jsonify({
        'ip_cliente': ip
    })

@app.route('/guardar-correccion', methods=['POST'])
def guardar_correccion():
    data = request.get_json()
    matricula = data.get('matricula')
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    db = get_db()
    db.execute('INSERT INTO correcciones (matricula, ip) VALUES (?, ?)', (matricula, ip))
    db.commit()
    db.close()
    return jsonify(success=True)

@app.route('/api/stats')
def api_stats():
    db = get_db()
    visitas = db.execute('SELECT COUNT(*) FROM visitas').fetchone()[0]
    usuarios = db.execute('SELECT COUNT(DISTINCT ip) FROM visitas').fetchone()[0]
    correcciones = db.execute('SELECT COUNT(*) FROM correcciones').fetchone()[0]
    db.close()
    return jsonify({
        'users': usuarios,
        'visits': visitas,
        'corrections': correcciones
    })

@app.before_request
def contar_visita():
    if request.endpoint not in ('static',):
        ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
        db = get_db()
        db.execute('INSERT INTO visitas (ip) VALUES (?)', (ip,))
        db.commit()
        db.close()

@app.route('/robots.txt')
def robots():
    return app.send_static_file('robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return app.send_static_file('sitemap.xml')

@app.route('/google935869f451a677c7.html')
def google_verification():
    return app.send_static_file('google935869f451a677c7.html')

if __name__ == '__main__':
    app.run()
