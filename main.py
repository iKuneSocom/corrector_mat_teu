from flask import Flask, request, jsonify, render_template
import re

app = Flask(__name__)
pattern = re.compile(r'^[A-Z]{4}\d{7}$')

last_corrections = []

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
    last_corrections = last_corrections[:9]

    return jsonify({
        'last_corrections': last_corrections,
        'ip_cliente': ip
    })

if __name__ == '__main__':
    app.run()
