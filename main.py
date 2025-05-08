from flask import Flask, request, jsonify, render_template
import re

app = Flask(__name__)

# Patrón regex para validar matrícula
pattern = re.compile(r'^[A-Z]{4}\d{7}$')

# Historial de las últimas 18 matrículas corregidas
last_corrections = []

def corregir_matricula(matricula):
    matricula_limpia = re.sub(r'[^A-Za-z0-9]', '', matricula).upper()
    es_valida = bool(pattern.match(matricula_limpia))
    return matricula_limpia, es_valida

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/validar', methods=['POST'])
def validar():
    data = request.json
    matricula = data.get('matricula', '')
    corregida, es_valida = corregir_matricula(matricula)

    global last_corrections
    last_corrections.insert(0, {'original': matricula, 'corregida': corregida, 'es_valida': es_valida})
    last_corrections = last_corrections[:18]

    respuesta = {
        'original': matricula,
        'corregida': corregida,
        'es_valida': es_valida,
        'last_corrections': last_corrections
    }

    return jsonify(respuesta)

if __name__ == '__main__':
    app.run(debug=True)
