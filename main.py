import os
import sqlite3
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import serial
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import database as db
from leitura import ErroSensor, parse_linha

PORTA = os.getenv("PORTA_SERIE", "/dev/ttyACM0")#/dev/ttyACM0" | hardcoded old port
STATIC = Path(__file__).parent / "static"

app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC), name="static")

# Ultima leitura do Arduino. So a thread de leitura escreve aqui; os pedidos so leem.
ultima = {"erro": "a espera da primeira leitura..."}

db.init_db()
db.apagar_antigas(7)


# Thread que le a porta serie para sempre e guarda cada leitura valida.
def ler_em_fundo():
    global ultima
    guardadas = 0
    while True:
        try:
            # Abrir a porta reinicia o Arduino: arranque (~2 s) + intervalo de 5 s. timeout=8 trata disso.
            with serial.Serial(PORTA, 9600, timeout = 8) as ser:
                ultima= {"erro": "arduino ligado, a espera da primeira leitura..."}

                while True:
                    # uma linha por leitura; vazia quando o timeout passa sem dados
                    line = ser.readline().decode(errors="replace").strip()

                    if not line:
                        ultima = {"erro": "sem dados do Arduino ha 8 s"}
                        continue
                    # um erro por tipo de problema; o ultimo estado fica em `ultima`
                    try:
                        t, h = parse_linha(line)
                        ultima = {"temperatura": t, "humidade": h}

                        try:
                            db.guardar(t, h)
                            # a cada 720 leituras (cerca de 1 h) limpa o que e antigo
                            guardadas += 1

                            if guardadas % 720 == 0:
                                db.apagar_antigas(7)
                        except sqlite3.Error as e:
                            ultima = {"erro": f"erro na base de dados: {e}"}

                    except ErroSensor:
                        ultima = {"erro": "sensor DHT sem leitura valida"}
                    except ValueError:
                        ultima = {"erro": f"leitura invalida: {line!r}"}

        except serial.SerialException: #as e: -descomenta isso debug
            # Arduino desligado ou porta ocupada: tenta abrir de novo em 2 s.
            ultima = {"erro": "Arduino desligado. A tentar de novo... "} # mete ({e}) no final e f no inicio antes do " se quiseres debug
            time.sleep(2)


threading.Thread(target=ler_em_fundo, daemon=True).start()


# ultima leitura do Arduino (503 se houver erro)
@app.get("/")
def root():
    if "erro" in ultima:
        raise HTTPException(503, ultima["erro"])
    return ultima


# a pagina
@app.get("/live")
def live():
    return FileResponse(STATIC / "live.html")


# media dos ultimos 15 min
@app.get("/media")
def media():
    temperatura, humidade = db.media()
    if temperatura is None:
        raise HTTPException(404, "sem leituras nos ultimos 15 min")
    return {"temperatura": temperatura, "humidade": humidade}


def _utc(d):
    """datetime do pedido -> 'YYYY-MM-DD HH:MM:SS' em UTC, como na base de dados. Sem fuso conta como UTC."""
    if d is None:
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


# minimo, media e maximo: ultimos N minutos ou um periodo (de/ate)
@app.get("/estatisticas")
def estatisticas(
    minutos: int = Query(60, ge=1, le=10080),
    de: datetime | None = None,
    ate: datetime | None = None,
):
    n, t_min, t_med, t_max, h_min, h_med, h_max = db.estatisticas(minutos, _utc(de), _utc(ate))
    if n == 0:
        raise HTTPException(404, "sem leituras nesse intervalo" if de else f"sem leituras nos ultimos {minutos} min")
    return {
        "leituras": n,
        "temperatura": {"min": t_min, "media": t_med, "max": t_max},
        "humidade": {"min": h_min, "media": h_med, "max": h_max},
    }


# as ultimas n leituras
@app.get("/historico")
def historico(n: int = Query(60, ge=1, le=1000)):
    return [
        {"hora": hora, "temperatura": t, "humidade": h}
        for hora, t, h in db.ultimas(n)
    ]


# medias em blocos de `passo` minutos
@app.get("/medias")
def medias(
    n: int = Query(30, ge=1, le=1000),
    passo: int = Query(1, ge=1, le=60),
    de: datetime | None = None,
    ate: datetime | None = None,
):
    if 60 % passo:
        raise HTTPException(422, "passo tem de dividir 60 (1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30 ou 60)")
    return [
        {"minuto": intervalo, "temperatura": t, "humidade": h}
        for intervalo, t, h in db.medias_por_intervalo(n, passo, _utc(de), _utc(ate))
    ]
