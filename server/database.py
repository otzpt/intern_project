# Base de dados SQLite. Cada funcao abre a sua ligacao porque a thread de leitura
# e os pedidos da API correm em threads diferentes.
import sqlite3
from contextlib import closing

DB = "reads.db"

# cria a tabela se ainda nao existir (corre no arranque)
def init_db():
    with closing(sqlite3.connect(DB)) as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS reads (
                id INTEGER PRIMARY KEY,
                temperatura REAL NOT NULL,
                humidade REAL NOT NULL,
                -- hora em UTC, preenchida pelo SQLite
                hora TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        con.commit()

# guarda uma leitura valida
def guardar(temperatura, humidade):
    with closing(sqlite3.connect(DB)) as con:
        con.execute(
            "INSERT INTO reads (temperatura, humidade) VALUES (?,?)",
            (temperatura, humidade),
        )
        con.commit()

# media dos ultimos `minutos` minutos; (None, None) se nao houver leituras
def media(minutos=15):
    with closing(sqlite3.connect(DB)) as con:
        return con.execute(
            "SELECT AVG(temperatura), AVG(humidade) FROM reads "
            "WHERE hora >= datetime('now', ?)",
            (f"-{minutos} minutes",),
        ).fetchone()

# as ultimas n leituras, da mais antiga para a mais nova
def ultimas(n=60):
    with closing(sqlite3.connect(DB)) as con:
        linhas = con.execute(
            "SELECT hora, temperatura, humidade FROM reads ORDER BY id DESC LIMIT ?",
        (n,),
        ).fetchall()
    return linhas[::-1]

def medias_por_intervalo(n=30, passo=1, de=None, ate=None):
    """Medias em blocos de `passo` minutos (um divisor de 60), os `n` mais recentes, do mais antigo para o mais novo.
    `de` e `ate` (UTC, 'YYYY-MM-DD HH:MM:SS') limitam o periodo: de incluido, ate excluido."""
    with closing(sqlite3.connect(DB)) as con:
        linhas = con.execute(
            "SELECT strftime('%Y-%m-%d %H:', hora) || "
            "printf('%02d', CAST(strftime('%M', hora) AS INTEGER) / :passo * :passo) AS intervalo, "
            "AVG(temperatura), AVG(humidade) "
            "FROM reads WHERE hora >= COALESCE(:de, '0000') AND hora < COALESCE(:ate, '9999') "
            "GROUP BY intervalo ORDER BY intervalo DESC LIMIT :n",
            {"passo": passo, "de": de, "ate": ate, "n": n},
        ).fetchall()
    return linhas[::-1]


def estatisticas(minutos=60, de=None, ate=None):
    """(n, t_min, t_media, t_max, h_min, h_media, h_max). Sem `de`, usa os ultimos `minutos`.
    Sem leituras: n=0 e o resto None."""
    with closing(sqlite3.connect(DB)) as con:
        return con.execute(
            "SELECT COUNT(*), MIN(temperatura), AVG(temperatura), MAX(temperatura), "
            "MIN(humidade), AVG(humidade), MAX(humidade) "
            "FROM reads WHERE hora >= COALESCE(?, datetime('now', ?)) AND hora < COALESCE(?, '9999')",
            (de, f"-{minutos} minutes", ate),
        ).fetchone()


# retencao: apaga o que tem mais de `dias` dias e devolve quantas linhas apagou
def apagar_antigas(dias = 7):
    with closing(sqlite3.connect(DB)) as con:
        apagadas = con.execute(
            "DELETE FROM reads WHERE hora < datetime('now', ?)",
            (f"-{dias} days",),
        ).rowcount
        con.commit()
    return apagadas
