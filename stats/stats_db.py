from flask import Flask, jsonify, request, render_template, Blueprint, send_file
import subprocess
import sys
import os
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth

# Si este archivo es independiente:
app = Flask(__name__)
CORS(app, origins=["https://www.pmap.app", "http://localhost:5000"])

# Si usas get_db de otro archivo, importa aquí:
from models import get_db

auth = HTTPBasicAuth()
try:
    from security import USERS
except ImportError:
    USERS = {
        os.environ.get("STATS_USER", "admin"): os.environ.get("STATS_PASS", "contraseña_predeterminada")
    }

@auth.verify_password
def verify_password(username, password):
    return USERS.get(username) == password

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
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 25))
    order = request.args.get('order', 'desc').lower()
    if order not in ('asc', 'desc'):
        order = 'desc'

    db = get_db()
    total = db.execute('SELECT COUNT(*) FROM correcciones').fetchone()[0]
    query = f'''
        SELECT matricula, ip, fecha
        FROM correcciones
        ORDER BY fecha {order.upper()}
        LIMIT ? OFFSET ?
    '''
    correcciones = db.execute(query, (per_page, (page-1)*per_page)).fetchall()
    db.close()
    return jsonify({
        'data': [dict(c) for c in correcciones],
        'total': total
    })

@stats_bp.route('/stats/api/contador_correcciones')
def contador_correcciones():
    db = get_db()
    total = db.execute('SELECT COUNT(*) FROM correcciones').fetchone()[0]
    db.close()
    return jsonify({'total': total})

@stats_bp.route('/stats/api/contadores')
def contadores():
    depurado = request.args.get('depurado', '0') == '1'
    db = get_db()
    # Visitas únicas (por IP) y totales
    if depurado:
        # Excluir IP del bot, por ejemplo '127.0.0.2' o la que uses para el bot
        bot_ip = '127.0.0.2'  # Cambia esto por la IP real del bot si es otra
        total_visitas = db.execute("SELECT COUNT(*) FROM visitas WHERE ip != ?", (bot_ip,)).fetchone()[0]
        visitas_unicas = db.execute("SELECT COUNT(DISTINCT ip) FROM visitas WHERE ip != ?", (bot_ip,)).fetchone()[0]
        total_correcciones = db.execute("SELECT COUNT(*) FROM correcciones WHERE ip != ?", (bot_ip,)).fetchone()[0]
    else:
        total_visitas = db.execute("SELECT COUNT(*) FROM visitas").fetchone()[0]
        visitas_unicas = db.execute("SELECT COUNT(DISTINCT ip) FROM visitas").fetchone()[0]
        total_correcciones = db.execute("SELECT COUNT(*) FROM correcciones").fetchone()[0]
    db.close()
    return jsonify({
        'visitas_unicas': visitas_unicas,
        'visitas_totales': total_visitas,
        'correcciones_totales': total_correcciones
    })

@stats_bp.route('/stats/api/todas_correcciones')
@auth.login_required
def todas_correcciones():
    db = get_db()
    datos = db.execute('SELECT * FROM correcciones ORDER BY fecha DESC').fetchall()
    db.close()
    return jsonify([dict(row) for row in datos])

@stats_bp.route('/stats/api/descargar_db')
@auth.login_required
def descargar_db():
    return send_file('stats.db', as_attachment=True)

app.register_blueprint(stats_bp)

if __name__ == '__main__':
    app.run()