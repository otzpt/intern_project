import threading
import time

import serial
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI()
PORTA = "/dev/ttyACM0"

# Ultima leitura do Arduino. So a thread de leitura escreve aqui; os pedidos so leem.
ultima = {"erro": "a espera da primeira leitura..."}


def ler_em_fundo():
    global ultima
    while True:
        try:
            with serial.Serial(PORTA, 9600, timeout = 8) as ser:
                ultima= {"erro": "arduino ligado, a espera da primeira leitura..."}
                while True:
                    line = ser.readline().decode(errors="replace").strip()
                    if not line:
                        ultima = {"erro": "sem dados do Arduino ha 8 s"}
                        continue
                    try:
                        t, h = line.split(",") # guardar temperatura e humidade
                        ultima = {"temperatura": float(t), "humidade": float(h)}
                    except ValueError:
                        ultima = {"erro": f"leitura invalida: {line!r}"}

        except serial.SerialException as e:
            # Arduino desligado ou porta ocupada: tenta abrir de novo em 2 s.
            ultima = {"erro": f"Arduino desligado? A tentar de novo... ({e})"}
            time.sleep(2)

threading.Thread(target=ler_em_fundo, daemon=True).start()

PAGINA = """
<!doctype html>
        <meta charset="utf-8">
            <title>Sensor</title>
            <p id="valores">A espera da primeira leitura...</p>
    <script>
        const el = document.getElementById("valores");
        async function atualizar() {
            try {
                const r = await fetch("/");
                const d = await r.json();
                el.textContent = r.ok ? `Temperatura: ${d.temperatura} °C | Humidade: ${d.humidade} %`: d.detail;
            } catch (e) {
                el.textContent = "Sem ligacao ao servidor";
            }
        }
        atualizar();
        setInterval(atualizar, 1000);
    </script>
"""


@app.get("/")
def root():
    if "erro" in ultima:
        raise HTTPException(503, ultima["erro"])
    return ultima


@app.get("/live", response_class=HTMLResponse)
def live():
    return PAGINA
