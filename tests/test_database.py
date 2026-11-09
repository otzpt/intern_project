import os
import sqlite3
import tempfile
import unittest
from contextlib import closing

from server import database as db


class TestDataBase(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

        db.DB = os.path.join(self.dir.name, "teste.db")
        db.init_db()

    def inserir(self, hora, t, h):
        with closing(sqlite3.connect(db.DB)) as con:
            con.execute("INSERT INTO reads (hora, temperatura, humidade) VALUES (?, ?, ?)", (hora, t, h))
            con.commit()

    def test_media_sem_leituras(self):
        self.assertEqual(db.media(), (None, None))

    def test_media_ignora_leituras_antigas(self):
        self.inserir("2000-01-01 00:00:00", 99.0, 99.0)

        db.guardar(20.0, 50.0)
        db.guardar(22.0, 60.0)

        self.assertEqual(db.media(15), (21.0, 55.0))

    def test_ultimas_mais_antiga_primeiro(self):
        for i in range(5):
            db.guardar(float(i), 50.0)

        self.assertEqual([t for _, t, _ in db.ultimas(3)], [2.0, 3.0, 4.0])

    def test_medias_por_minuto_agrupa(self):
        self.inserir("2026-11-06 12:00:05", 20.0, 50.0)
        self.inserir("2026-11-06 12:00:35", 22.0, 60.0)
        self.inserir("2026-11-06 12:01:10", 30.0, 70.0)
        self.assertEqual(
            db.medias_por_intervalo(5),
            [("2026-11-06 12:00", 21.0, 55.0), ("2026-11-06 12:01", 30.0, 70.0)],
        )

    def test_apagar_antigas(self):
        self.inserir("2000-01-01 00:00:00", 99.0, 99.0)
        db.guardar(20.0, 50.0)

        self.assertEqual(db.apagar_antigas(7), 1)
        self.assertEqual(len(db.ultimas(10)), 1)
    def test_estatisticas(self):
        self.inserir("2000-01-01 00:00:00", 99.0, 99.0)
        db.guardar(20.0, 50.0)
        db.guardar(24.0, 70.0)

        self.assertEqual(db.estatisticas(60), (2, 20.0, 22.0, 24.0, 50.0, 60.0, 70.0))

    def test_estatisticas_sem_leituras(self):
        self.assertEqual(db.estatisticas(60), (0, None, None, None, None, None, None))

    def test_medias_por_intervalo_passo(self):
        self.inserir("2026-11-06 12:02:00", 20.0, 50.0)
        self.inserir("2026-11-06 12:04:00", 22.0, 60.0)
        self.inserir("2026-11-06 12:07:00", 30.0, 70.0)
        self.assertEqual(
            db.medias_por_intervalo(5, passo=5),
            [("2026-11-06 12:00", 21.0, 55.0), ("2026-11-06 12:05", 30.0, 70.0)],
        )

    def test_intervalo_de_ate(self):
        self.inserir("2026-11-05 23:59:59", 1.0, 1.0)
        self.inserir("2026-11-06 00:00:00", 20.0, 50.0)
        self.inserir("2026-11-06 23:59:59", 24.0, 70.0)
        self.inserir("2026-11-07 00:00:00", 99.0, 99.0)
        de, ate = "2026-11-06 00:00:00", "2026-11-07 00:00:00"

        self.assertEqual(db.estatisticas(de=de, ate=ate), (2, 20.0, 22.0, 24.0, 50.0, 60.0, 70.0))
        self.assertEqual(len(db.medias_por_intervalo(100, de=de, ate=ate)), 2)


if __name__ == "__main__":
    unittest.main()
