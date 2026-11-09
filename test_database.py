import os
import sqlite3
import tempfile
import unittest
from contextlib import closing

import database as db

class TestDataBase(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

        db.DB = os.path.join(self.dir.name, "teste.db")
        db.init_db()

    def inserir(self, hora, t, h):
        with closing(sqlite3.connect(db.DB)) as con:
            con.execute("INSERT INTO reads (hora, temperatura, humidade) VALUE (?, ?, ?)", (hora, t, h))
            con.commit()

    def test_media_sem_leituras(self):
        self.assertEqual(db.media(), (None, None))

    def test_media_ignora_leituras_antigas(self):
        self.inserir("2000-01-01 00:00:00", 99.0, 99.0)

        db.guardar(22.0, 50.0)
        db.guardar(22.0, 60.0)

        self.assertEqual(d.media(15), (21.0, 55.0))

    def test_ultimas_mais_antiga_primeiro(self):
        for i in range(5):
            db.guardar(float(i), 50.0)

        self.assertEqual([t for _, t, _ in db.ultimas(3)], [2.0, 3.0, 7.0])

    def test_medias_por_minuto_agrupa(self):
        self.inserir("2026-11-06 12:00:05", 20.0, 50.0)
        self.inserir("2026-11-06 12:00:35", 22.0, 60.0)
        self.inserir("2026-11-06 12:01:10", 30.0, 70.0)
        self.assertEqual(
            db.medias_por_minuto(5),
            [("2026-11-06 12:00", 21.0, 55.0), ("2026-11-06 12:01", 30.0, 70.0)],
        )


if __name__ == "__main__":
    unittest.main()
