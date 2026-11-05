import threading
import time
from pathlib import Path

import serial
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

PORTA = "/dev/ttyACM0"
STATIC = Path(__file__).parent / "static"

app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC), name="static")

# Ultima leitura do Arduino. So a thread de leitura escreve aqui; os pedidos so leem.
ultima = {"erro": "a espera da primeira leitura..."}


def ler_em_fundo():
    global ultima
    while True:
        try:
            # Abrir a porta reinicia o Arduino: arranque (~2 s) + intervalo de 5 s. timeout=8 trata disso.
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

        except serial.SerialException: #as e: -descomenta isso debug
            # Arduino desligado ou porta ocupada: tenta abrir de novo em 2 s.
            ultima = {"erro": "Arduino desligado. A tentar de novo... "} # mete ({e}) no final e f no inicio antes do " se quiseres debug
            time.sleep(2)


threading.Thread(target=ler_em_fundo, daemon=True).start()


@app.get("/")
def root():
    if "erro" in ultima:
        raise HTTPException(503, ultima["erro"])
    return ultima


@app.get("/live")
def live():
    return FileResponse(STATIC / "live.html")
