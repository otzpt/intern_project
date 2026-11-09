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
| `sensor DHT sem leitura valida` | The Arduino printed `Erro a ler o DHT` |
| `leitura invalida: '<line>'` | Line is not `temperatura,humidade` |
| `Arduino desligado. A tentar de novo... ` | Port could not be opened, retries every 2 s |
| `erro na base de dados: <error>` | The reading was valid but saving it failed |

### `GET /media`

Average of the readings saved in the last 15 minutes.

```json
{"temperatura": 21.9, "humidade": 39.7}
```

Returns `404` with `{"detail": "sem leituras nos ultimos 15 min"}` when the window has no readings. The average covers only the readings that exist, so right after startup it is shorter than 15 minutes.

### `GET /historico?n=60`

The last `n` saved readings, oldest first. `n` is an integer from 1 to 1000 (default 60), anything else returns `422`.

```json
[{"hora": "2026-11-06 12:54:13", "temperatura": 22.9, "humidade": 39.4}]
```

`hora` is UTC, `YYYY-MM-DD HH:MM:SS`. Returns `[]` when the table is empty.

### `GET /medias?n=30`

Per-minute averages of the last `n` minutes that have readings, oldest first. `n` has the same limits as `/historico`.

```json
[{"minuto": "2026-11-06 12:54", "temperatura": 22.9, "humidade": 39.5}]
```

The newest entry is the minute in progress, so its average is incomplete.

### `GET /live`

HTML page (`static/live.html`). It polls `/` and `/media` every second, `/historico?n=60` every 5 s and `/medias?n=15` every 60 s, and draws four SVG charts (temperature and humidity, current and per-minute average). Static files are served from `/static`.

## Database

SQLite file `reads.db`, created on startup in the folder the server runs from. It is in `.gitignore`.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | Primary key |
| `temperatura` | REAL | Celsius |
| `humidade` | REAL | Percent |
| `hora` | TEXT | `CURRENT_TIMESTAMP`, UTC, `YYYY-MM-DD HH:MM:SS` |

Only valid readings are saved. `database.py` opens a new connection per call, because the reading thread and the request threads cannot share one SQLite connection by default.
