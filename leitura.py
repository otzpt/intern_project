import math


class ErroSensor(ValueError):
    """O Arduino diz que o DHT falhou a ler."""


def parse_linha(linha):
    """'21.90,39.70' -> (21.9, 39.7). Levanta ValueError caso a linha seja invalida"""
    if linha.startswith("Erro a ler"):
        raise ErroSensor(linha)

    t, h = linha.split(",")
    t, h = float(t), float(h)

    if not (math.isfinite(t) and math.isfinite(h)):
        raise ValueError(f"valor nao finito: {linha!r}")

    return t, h
