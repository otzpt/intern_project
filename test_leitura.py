import unittest

from leitura import parse_linha


class TestParseLinha(unittest.TestCase):
    def test_linha_valida(self):
        self.assertEqual(parse_linha("21.90,39.70"), (21.9, 39.7))

    def test_linhas_invalidas(self):
        for linha in ["Erro a ler DHT", "1,2,3", "abc,def", "", ",", "nan,40", "20,inf"]:
            with self.subTest(linha=linha), self.assertRaises(ValueError):
                parse_linha(linha)

if __name__ == "__main__":
    unittest.main()
