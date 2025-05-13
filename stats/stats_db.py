from flask import Flask, jsonify, request, render_template, Blueprint
import subprocess
import sys
import os

# Si este archivo es independiente:
app = Flask(__name__)

# Si usas get_db de otro archivo, importa aquí:
from models import get_db

stats_bp = Blueprint('stats', __name__, template_folder='../templates')

bot_process = None

@stats_bp.route('/stats/')
def stats_home():
    return render_template('stats_db.html')

@stats_bp.route('/stats/api/bot_status')
def bot_status():
    global bot_process
    return jsonify({'running': bot_process is not None and bot_process.poll() is None})

@stats_bp.route('/stats/api/toggle_bot', methods=['POST'])
def toggle_bot():
    global bot_process
    if bot_process is not None and bot_process.poll() is None:
        bot_process.terminate()
        bot_process = None
        return jsonify({'running': False})
    else:
        bot_process = subprocess.Popen(
            ['python', 'dev_training/pmap_test_bot.py'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return jsonify({'running': True})

@stats_bp.route('/stats/api/correcciones')
def api_correcciones():
    ip = request.args.get('ip')
    letras = request.args.get('letras')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))

    db = get_db()
    query = 'SELECT COUNT(*) FROM correcciones WHERE 1=1'
    params = []
    if ip:
        query += ' AND ip = ?'
        params.append(ip)
    if letras:
        query += ' AND matricula LIKE ?'
        params.append(f'{letras.upper()}%')
    total = db.execute(query, params).fetchone()[0]

    query = 'SELECT matricula, ip, fecha FROM correcciones WHERE 1=1'
    params = []
    if ip:
        query += ' AND ip = ?'
        params.append(ip)
    if letras:
        query += ' AND matricula LIKE ?'
        params.append(f'{letras.upper()}%')
    query += ' ORDER BY fecha DESC LIMIT ? OFFSET ?'
    params.extend([per_page, (page-1)*per_page])
    correcciones = db.execute(query, params).fetchall()
    db.close()
    return jsonify({
        'data': [dict(c) for c in correcciones],
        'total': total
    })

app.register_blueprint(stats_bp)

if __name__ == '__main__':
    app.run()