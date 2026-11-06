# API

Server: FastAPI, started with `uvicorn main:app` (default `http://127.0.0.1:8000`).

## Routes

### `GET /`

Last reading from the Arduino.

```json
{"temperatura": 21.9, "humidade": 39.7}
```

Errors return `503` with `{"detail": "<message>"}`. Messages in `main.py`:

| Message | Meaning |
|---|---|
| `a espera da primeira leitura...` | Server just started, nothing read yet |
| `arduino ligado, a espera da primeira leitura...` | Port opened, Arduino is rebooting (about 7 s) |
| `sem dados do Arduino ha 8 s` | Port is open but no line arrived in 8 s |
| `leitura invalida: '<line>'` | Line is not `temperatura,humidade` (includes the Arduino's own `Erro a ler o DHT`) |
| `Arduino desligado. A tentar de novo... ` | Port could not be opened, retries every 2 s |
| `erro na base de dados: <error>` | The reading was valid but saving it failed |

### `GET /media`

Average of the readings saved in the last 15 minutes.

```json
{"temperatura": 21.9, "humidade": 39.7}
```

Returns `404` with `{"detail": "sem leituras nos ultimos 15 min"}` when the window has no readings. The average covers only the readings that exist, so right after startup it is shorter than 15 minutes.

### `GET /live`

HTML page (`static/live.html`) that polls `/` and `/media` every second. Static files are served from `/static`.

## Database

SQLite file `reads.db`, created on startup in the folder the server runs from. It is in `.gitignore`.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | Primary key |
| `temperatura` | REAL | Celsius |
| `humidade` | REAL | Percent |
| `hora` | TEXT | `CURRENT_TIMESTAMP`, UTC, `YYYY-MM-DD HH:MM:SS` |

Only valid readings are saved. `database.py` opens a new connection per call, because the reading thread and the request threads cannot share one SQLite connection by default.
