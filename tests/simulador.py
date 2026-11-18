import os
import pty
import random
import time

master, slave = pty.openpty() # master e o codigo que vez, slave e a porta serie simulada
caminho = os.ttyname(slave) # traduz slave para um caminho

print(caminho)

while True:
    # valores aleatorios para ser um teste simulado mais autentico
    temp = random.uniform(15, 30)
    humidade = random.uniform(30, 50)

    # erro retorna true caso o numero aleatorio de 0 a 1 for menor que 0.1
    erro = random.random() < 0.1
    if erro:
        os.write(master, "Erro a ler o DHT\r\n".encode())
    else:
        os.write(master, f"{temp:.1f},{humidade:.1f}\r\n".encode()) # simular valores

    time.sleep(5)
