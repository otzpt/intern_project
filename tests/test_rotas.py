import os
import tempfile
import unittest

from fastapi.testclient import TestClient

from server import database as db
from server import main


class TestRotas(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)

        db.DB = os.path.join(self.dir.name, "teste.db")
        db.init_db()

        # a thread de leitura nao corre aqui, por isso o estado do Arduino e o que o teste puser
        guardada = main.ultima
        self.addCleanup(setattr, main, "ultima", guardada)

        # sem `with`, o TestClient nao corre o lifespan (nem a thread, nem a porta serie)
        self.client = TestClient(main.app)

    def test_estado_sem_leituras(self):
        r = self.client.get("/estado")
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.assertEqual(d["leituras"], 0)
        self.assertIsNone(d["primeira"])
        self.assertIsNone(d["ultima_leitura"])

    def test_estado_mostra_o_erro_do_arduino(self):
        main.ultima = {"erro": "Arduino desligado. A tentar de novo... "}
        r = self.client.get("/estado")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["arduino"], "Arduino desligado. A tentar de novo... ")

    def test_raiz_com_leitura(self):
        main.ultima = {"temperatura": 22.5, "humidade": 40.1}
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"temperatura": 22.5, "humidade": 40.1})

    def test_raiz_com_erro_da_503(self):
        main.ultima = {"erro": "sensor DHT sem leitura valida"}
        r = self.client.get("/")
        self.assertEqual(r.status_code, 503)
        self.assertEqual(r.json()["detail"], "sensor DHT sem leitura valida")

    def test_media_sem_leituras_da_404(self):
        self.assertEqual(self.client.get("/media").status_code, 404)

    def test_media_com_leituras(self):
        db.guardar(20.0, 40.0)
        db.guardar(22.0, 50.0)
        r = self.client.get("/media")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"temperatura": 21.0, "humidade": 45.0})

    def test_historico_vazio(self):
        r = self.client.get("/historico")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), [])

    def test_historico_devolve_as_leituras_guardadas(self):
        db.guardar(20.0, 40.0)
        db.guardar(22.0, 50.0)
        r = self.client.get("/historico?n=10")
        self.assertEqual([x["temperatura"] for x in r.json()], [20.0, 22.0])

    def test_historico_n_fora_dos_limites_da_422(self):
        self.assertEqual(self.client.get("/historico?n=0").status_code, 422)
        self.assertEqual(self.client.get("/historico?n=1001").status_code, 422)

    def test_medias_passo_que_nao_divide_60_da_422(self):
        self.assertEqual(self.client.get("/medias?passo=7").status_code, 422)
        self.assertEqual(self.client.get("/medias?passo=0").status_code, 422)

    def test_estatisticas_sem_leituras_da_404(self):
        self.assertEqual(self.client.get("/estatisticas").status_code, 404)

    def test_rota_que_nao_existe_da_404(self):
        self.assertEqual(self.client.get("/nada").status_code, 404)


if __name__ == "__main__":
    unittest.main()
