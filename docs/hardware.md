# Hardware and serial protocol

## Parts

- Arduino connected by USB (appears as `/dev/ttyACM0` on Linux, override with the `PORTA_SERIE` environment variable, read in `server/main.py`)
- DHT22 temperature and humidity sensor, data pin on Arduino pin 2

Power, ground and any pull-up resistor wiring are not described by the code, so they are not documented here.

## Firmware

`arduino/main/main.ino` uses the `DHT.h` library, `DHT22` on pin 2, serial at 9600 baud. Every 5 s it reads the sensor and prints one line:

```
21.90,39.70
```

Format: `temperatura,humidade`, decimal point, two decimals (the default of `Serial.print` for floats), line ends with a newline.

If either value is `NaN`, it prints `Erro a ler o DHT` instead. The server shows that as `sensor DHT sem leitura valida`.

## Timing

Opening the serial port resets the Arduino. After that:

1. The board takes about 2 s to start.
2. The first reading is printed up to 5 s later.

The server reads with `timeout=8`, which covers both. If the cable is unplugged, the port read raises `SerialException`. The reader thread catches it, reports the error and tries to reopen the port every 2 s.
