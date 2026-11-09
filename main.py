import os
import sqlite3
import threading
import time
from pathlib import Path

import serial
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import database as db
from leitura import parse_linha

PORTA = os.getenv("PORTA_SERIE", "/dev/ttyACM0")#/dev/ttyACM0" | hardcoded old port
STATIC = Path(__file__).parent / "static"

app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC), name="static")

# Ultima leitura do Arduino. So a thread de leitura escreve aqui; os pedidos so leem.
ultima = {"erro": "a espera da primeira leitura..."}

db.init_db()


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
                        t, h = parse_linha(line)
                        ultima = {"temperatura": t, "humidade": h}

                        try:
                            db.guardar(t, h)
                        except sqlite3.Error as e:
                            ultima = {"erro": f"erro na base de dados: {e}"}
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


@app.get("/media")
def media():
    temperatura, humidade = db.media()
    if temperatura is None:
        raise HTTPException(404, "sem leituras nos ultimos 15 min")
    return {"temperatura": temperatura, "humidade": humidade}


@app.get("/historico")
def historico(n: int = Query(60, ge=1, le=1000)):
    return [
        {"hora": hora, "temperatura": t, "humidade": h}
        for hora, t, h in db.ultimas(n)
    ]


@app.get("/medias")
def medias(n : int = Query(30, ge=1, le=1000)):
    return [
        {"minuto": minuto, "temperatura": t, "humidade": h}
        for minuto, t, h in db.medias_por_minuto(n)
    ]
