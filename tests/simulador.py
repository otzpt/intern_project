import os
import pty
import random
import sys
import time


def ler_modo():
    modo = sys.argv[1] if len(sys.argv) > 1 else "normal"
    print(modo)
    return modo

def preso(temp, hum, n):
    return temp, hum

def deriva(temp, hum, n):
    dif_temp = random.gauss(0, 0.2)
    dif_hum = random.gauss(0, 0.5)

    # SIMPLIFICACAO: subida em linha reta, sem limite. A humidade chega a 0 por volta da volta 1200 (cerca de 100 min), por isso so serve para corridas curtas
    temp += dif_temp + 0.02 * n
    hum += dif_hum - 0.05 * n # a temperatura sobe e a humidade desce, 2.5 por grau como no pico

    return temp, hum

def pico(temp, hum, n):# idk if i should ask for a base value for now im keeping this like this and user gives the n as 0 so it doesnt reset everytime, after a while i might ask for both starting n and base_n to set how many repetions for till ruido comes trough
    # valores alterados para soma e subtraçao
    dif_temp = random.gauss(0, 0.2)
    dif_hum = random.gauss(0, 0.5)

    if n % 5 == 0:
        # gera o pico
        ruido_temp = random.choice([-11, -6, 6, 11])

        temp += ruido_temp
        # SIMPLIFICACAO: a humidade relativa desce cerca de 2.5 pontos por cada +1 C (aproximado, nao exato)
        hum -= ruido_temp * 2.5
    else:
        temp += dif_temp
        hum += dif_hum

    return temp, hum

def ruido(temp, hum, n):
    dif_temp = random.gauss(0, 0.9)
    dif_hum = random.gauss(0, 1.1)

    temp += dif_temp
    hum += dif_hum

    return temp, hum

def normal(temp, hum, n):
    # valores aleatorios para ser um teste simulado mais autentico
    dif_temp = random.gauss(0, 0.2)
    dif_hum = random.gauss(0, 0.5)

    temp += dif_temp
    hum += dif_hum

    return temp, hum

MODOS = {
    "normal": normal,
    "ruido": ruido,
    "pico": pico,
    "preso": preso,
    "deriva": deriva,
}

if __name__ == "__main__":
    modo = ler_modo()

    if modo not in MODOS:
        sys.exit(f"modo desconhecido: {modo}. modos validos: {', '.join(MODOS)}")

    master, slave = pty.openpty() # master e o codigo que vez, slave e a porta serie simulada
    caminho = os.ttyname(slave) # traduz slave para um caminho

    print(caminho)

    n = 0
    while True:
        temp, humidade = MODOS[modo](22.0, 60.0, n)

        # erro retorna true caso o numero aleatorio de 0 a 1 for menor que 0.1
        erro = random.random() < 0.1

        if erro:
            os.write(master, "Erro a ler o DHT\r\n".encode())
        else:
            os.write(master, f"{temp:.1f},{humidade:.1f}\r\n".encode()) # simular valores

        n += 1
        time.sleep(5)
