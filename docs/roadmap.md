# Roadmap

Proposals, not commitments. Each item says what in the code would change.

## Done

- DHT22 on an Arduino, one line per reading over serial
- Server reads the port, reconnects when the cable is unplugged, saves valid readings in SQLite
- Routes `/`, `/media`, `/historico`, `/medias`, `/live`
- Live page with temperature and humidity charts (last 60 readings and per-minute averages), dark mode

## Next sensors (CO2, gas)

The line format is fixed to two numbers: `t, h = line.split(",")` in `server/main.py` fails with a `ValueError` on any extra field, and the table `reads` has only `temperatura` and `humidade`.

1. Choose a line format that can grow, for example `temperatura=21.9,humidade=39.7,co2=612`.
2. Update the parser in `server/main.py` and the tables in `server/database.py`.
3. Add the new fields to `/`, `/historico`, `/medias` and `docs/api.md`.
4. Add one more chart per quantity in `server/static/live.html` and an entry in `GRAFICOS_ATUAL` and `GRAFICOS_MEDIA` in `server/static/script.js`.

## Other computers (host)

- The serial port is set with `PORTA_SERIE`. Typical names are `/dev/ttyACM0` or `/dev/ttyUSB0` on Linux, `COM3` and similar on Windows, `/dev/cu.usbmodem*` on macOS. Not tested outside Linux.
- Reading the port may need permissions for your user on Linux.
- `requirements.txt` pins the versions installed in the original `.venv` (Python 3.14). The minimum Python version that works is unknown, test it before relying on an older one.

## Other boards (ESP32, Nano, others)

The protocol does not depend on the board: any board that prints `temperatura,humidade` once per line at 9600 baud works with the server as it is.

- The baud rate `9600` is hardcoded in `server/main.py` (`serial.Serial(PORTA, 9600, ...)`) and in `arduino/main/main.ino`. A different rate needs both changed. Making it an environment variable like `PORTA_SERIE` would avoid editing the code.
- The sketch uses the `DHT.h` library and pin 2. Other boards may use different pin numbers.

## More than one device

Today there is one port, one reader thread and one table with no device column. For several devices:

1. Add a `dispositivo` column to `reads`.
2. Start one reader thread per port, each with its own entry in the shared `ultima` state.
3. Add a `?dispositivo=` filter to the routes and a selector to the page.

## Wireless instead of USB

A board with Wi-Fi could send each reading with an HTTP `POST` instead of the serial port. That needs a new route in `server/main.py` that validates the body, and a decision on authentication, since the server has none now.

## Tests

```bash
python -m unittest -v
```
