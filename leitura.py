import math


def parse_linha(linha):
    """'21.90,39.70' -> (21.9, 39.7). Levanta ValueError caso a linha seja invalida"""
    t, h = linha.split(",")
    t, h = float(t), float(h)

    if not (math.isfinite(t) and math.isfinite(h)):
        raise ValueError(f"valor nao finito: {linha!r}")

    return t, h
