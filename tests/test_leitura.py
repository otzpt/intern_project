import unittest

from server.leitura import ErroSensor, parse_linha


class TestParseLinha(unittest.TestCase):
    def test_linha_valida(self):
        self.assertEqual(parse_linha("21.90,39.70"), (21.9, 39.7))

    def test_linhas_invalidas(self):
        for linha in ["Erro a ler o DHT", "1,2,3", "abc,def", "", ",", "nan,40", "20,inf"]:
            with self.subTest(linha=linha), self.assertRaises(ValueError):
                parse_linha(linha)

    def test_erro_do_sensor(self):
        with self.assertRaises(ErroSensor):
            parse_linha("Erro a ler o DHT")

if __name__ == "__main__":
    unittest.main()
