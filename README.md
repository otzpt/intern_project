# intern_project

A simple car sensor monitor for my internship: an Arduino reads the sensors, a small FastAPI server stores the readings and shows them on a web page

Goal is temperature, humidity, CO2 and gas. Right now only temperature and humidity work.

## Features

- **Temperature and humidity**: DHT22 on pin 2, read every 5 s by `arduino/main/main.ino`
- **Live page**: `/live` shows the current reading against the 15 min average, live charts, averages and min/average/max statistics for several periods, and any one of the last 7 days on its own, with a dark mode switch that is remembered
- **History**: every valid reading is saved in SQLite (`reads.db`, created on startup), so the average survives a server restart. Readings older than 7 days are deleted
- **Reconnects by itself**: unplug the Arduino and the page shows an error, plug it back and it recovers with no restart
- **Routes**: `/` last reading as JSON (503 on error), `/media` average of the last 15 min (404 if there are no readings), `/historico` the last N readings, `/medias` averages in blocks of N minutes, `/estatisticas` min/average/max (last N minutes or a fixed period), `/live` the page

## How to run

You need an Arduino with the sketch from `arduino/main/main.ino` and a DHT22 on pin 2, plugged in by USB. The serial port is read from the `PORTA_SERIE` environment variable (default `/dev/ttyACM0`), e.g. `PORTA_SERIE=/dev/ttyUSB0 uvicorn server.main:app`.

```bash
git clone "https://github.com/otzpt/intern_project" && cd intern_project
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn server.main:app
```

Then open `http://127.0.0.1:8000/live`.

## Tests

```bash
.venv/bin/python -m unittest -v
```

## Limitations

Only temperature and humidity for now, CO2 and gas are not done

No authentication, anyone on the network can read the data if you bind it to `0.0.0.0`

## Docs

- [API and database](docs/api.md)
- [Hardware and serial protocol](docs/hardware.md)
- [Roadmap](docs/roadmap.md)
- [Code of conduct](CODE_OF_CONDUCT.md)

## License

[MIT](LICENSE)
