# Le as linhas que o Arduino envia. Fica fora do main.py para se poder testar.
import math


class ErroSensor(ValueError):
    """O Arduino diz que o DHT falhou a ler."""


def parse_linha(linha):
    """'21.90,39.70' -> (21.9, 39.7). Levanta ValueError caso a linha seja invalida"""
    # o Arduino escreve isto quando o DHT falha
    if linha.startswith("Erro a ler"):
        raise ErroSensor(linha)

    # split e float levantam ValueError se a linha nao for 'numero,numero'
    t, h = linha.split(",")
    t, h = float(t), float(h)

    # nan e inf sao floats validos em Python mas nao servem como leitura
    if not (math.isfinite(t) and math.isfinite(h)):
        raise ValueError(f"valor nao finito: {linha!r}")

    return t, h
