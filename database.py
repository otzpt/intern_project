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
