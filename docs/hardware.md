# Hardware e protocolo série

## Componentes

- Arduino ligado por USB (aparece como `/dev/ttyACM0` em Linux, pode ser alterado com a variável de ambiente `PORTA_SERIE`, lida em `server/main.py`)
- Sensor de temperatura e humidade DHT22, pino de dados no pino 2 do Arduino

A alimentação, a massa e a eventual resistência pull-up não estão descritas no código, por isso não estão documentadas aqui.

## Firmware

`arduino/main/main.ino` usa a biblioteca `DHT.h`, um `DHT22` no pino 2 e série a 9600 baud. De 5 em 5 s lê o sensor e escreve uma linha:

```
21.90,39.70
```

Formato: `temperatura,humidade`, ponto decimal, duas casas decimais (o comportamento por defeito do `Serial.print` com floats), a linha termina com uma mudança de linha.

Se um dos valores for `NaN`, escreve `Erro a ler o DHT`. O servidor mostra isso como `sensor DHT sem leitura valida`.

## Tempos

Abrir a porta série reinicia o Arduino. Depois disso:

1. A placa demora cerca de 2 s a arrancar.
2. A primeira leitura é escrita até 5 s mais tarde.

O servidor lê com `timeout=8`, o que cobre os dois. Se o cabo for desligado, a leitura da porta levanta `SerialException`. A thread de leitura apanha-a, regista o erro e tenta reabrir a porta de 2 em 2 s.
