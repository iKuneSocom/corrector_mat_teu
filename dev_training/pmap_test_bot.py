import random
import string
import time
import json
import urllib.request

URL = "https://www.pmap.app/guardar"
CORRECCIONES_POR_HORA = 20
INTERVALO_SEGUNDOS = 3600 / CORRECCIONES_POR_HORA

def generar_matricula():
    letra_extra = random.choice(string.ascii_uppercase)
    digitos = ''.join(random.choices(string.digits, k=7))
    return f"POW{letra_extra}{digitos}"

def enviar_matricula(matricula):
    payload = {
        "corregida": matricula,
        "hora_local": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(URL, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            resp_text = response.read().decode('utf-8')
            print(f"Enviada: {matricula} | Status: {response.status} | Respuesta: {resp_text}")
    except Exception as e:
        print(f"Error al enviar matrícula: {e}")

def bucle_pruebas():
    try:
        while True:
            matricula = generar_matricula()
            enviar_matricula(matricula)
            time.sleep(INTERVALO_SEGUNDOS)
    except KeyboardInterrupt:
        print("Finalizando...")

if __name__ == "__main__":
    bucle_pruebas()
