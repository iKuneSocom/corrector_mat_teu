from flask import Flask, request, jsonify, render_template
import os
import json

app = Flask(__name__)
STATS_FILE = 'stats.json'

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def api_stats():
    stats = load_stats()
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if user_ip not in stats['users']:
        stats['users'].add(user_ip)
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
    app.run(debug=True)