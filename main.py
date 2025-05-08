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
    ip_cliente = request.remote_addr

    global last_corrections
    last_corrections.insert(0, {
        'original': matricula,
        'corregida': corregida,
        'es_valida': es_valida,
        'ip': ip_cliente
    })
    last_corrections = last_corrections[:9]

    return jsonify({
        'original': matricula,
        'corregida': corregida,
        'es_valida': es_valida,
        'last_corrections': last_corrections,
        'ip_cliente': ip_cliente
    })

if __name__ == '__main__':
    app.run()
