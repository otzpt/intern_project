# intern_project

A simple car sensor monitor for my internship: an Arduino reads the sensors, a small FastAPI server stores the readings and shows them on a web page

Goal is temperature, humidity, CO2 and gas. Right now only temperature and humidity work.

## Features

- **Temperature and humidity**: DHT22 on pin 2, read every 5 s by `main/main.ino`
- **Live page**: `/live` shows the current reading and the 15 min average, with a dark mode switch
- **History**: every valid reading is saved in SQLite (`reads.db`, created on startup), so the average survives a server restart
- **Reconnects by itself**: unplug the Arduino and the page shows an error, plug it back and it recovers with no restart
- **Routes**: `/` last reading as JSON (503 on error), `/media` average of the last 15 min (404 if there are no readings), `/live` the page

## How to run

You need an Arduino with the sketch from `main/main.ino` and a DHT22 on pin 2, plugged in by USB. The serial port is hardcoded as `PORTA` in `main.py` (`/dev/ttyACM0`).

```bash
git clone "https://github.com/otzpt/intern_project" && cd intern_project
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app
```

Then open `http://127.0.0.1:8000/live`.

## Limitations

Serial port is hardcoded

Only temperature and humidity for now, CO2 and gas are not done

A DHT read error is shown as "leitura invalida", it is not told apart from a bad line

No authentication, anyone on the network can read the data if you bind it to `0.0.0.0`

## License

[MIT](LICENSE)
