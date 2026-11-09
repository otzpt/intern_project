import sqlite3
from contextlib import closing

DB = "reads.db"

def init_db():
    with closing(sqlite3.connect(DB)) as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS reads (
                id INTEGER PRIMARY KEY,
                temperatura REAL NOT NULL,
                humidade REAL NOT NULL,
                hora TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        con.commit()

def guardar(temperatura, humidade):
    with closing(sqlite3.connect(DB)) as con:
        con.execute(
            "INSERT INTO reads (temperatura, humidade) VALUES (?,?)",
            (temperatura, humidade),
        )
        con.commit()

def media(minutos=15):
    with closing(sqlite3.connect(DB)) as con:
        return con.execute(
            "SELECT AVG(temperatura), AVG(humidade) FROM reads "
            "WHERE hora >= datetime('now', ?)",
            (f"-{minutos} minutes",),
        ).fetchone()

def ultimas(n=60):
    with closing(sqlite3.connect(DB)) as con:
        linhas = con.execute(
            "SELECT hora, temperatura, humidade FROM reads ORDER BY id DESC LIMIT ?",
        (n,),
        ).fetchall()
    return linhas[::-1]

def medias_por_minuto(n=30):
    with closing(sqlite3.connect(DB)) as con:
        linhas = con.execute(
            "SELECT strftime('%Y-%m-%d %H:%M', hora) AS minuto, "
            "AVG(temperatura), AVG(humidade) "
            "FROM reads GROUP BY minuto ORDER BY minuto DESC LIMIT ?",
            (n,),
        ).fetchall()
    return linhas[::-1]

def apagar_antigas(dias = 7):
    with closing(sqlite3.connect(DB)) as con:
        apagadas = con.execute(
            "DELETE FROM reads WHERE hora < datetime('now', ?)",
            (f"-{dias} days",),
        ).rowcount
        con.commit()
    return apagadas
