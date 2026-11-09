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

### `GET /estatisticas?minutos=60`

Minimum, average and maximum of the saved readings. `minutos` is an integer from 1 to 10080 (default 60): the window ends now. Alternatively `de` and `ate` pick a fixed period, as ISO 8601 datetimes (`2026-11-09T00:00:00Z`, no zone counts as UTC). `de` is included, `ate` is excluded, and `minutos` is ignored when `de` is given. Anything invalid returns `422`.

```json
{"leituras": 711, "temperatura": {"min": 19.7, "media": 20.1, "max": 20.9}, "humidade": {"min": 62.0, "media": 64.1, "max": 67.0}}
```

Returns `404` with `{"detail": "sem leituras nos ultimos <minutos> min"}` (or `"sem leituras nesse intervalo"` with `de`) when the period has no readings.

### `GET /historico?n=60`

The last `n` saved readings, oldest first. `n` is an integer from 1 to 1000 (default 60), anything else returns `422`.

```json
[{"hora": "2026-11-06 12:54:13", "temperatura": 22.9, "humidade": 39.4}]
```

`hora` is UTC, `YYYY-MM-DD HH:MM:SS`. Returns `[]` when the table is empty.

### `GET /medias?n=30&passo=1`

Averages in blocks of `passo` minutes, the last `n` blocks that have readings, oldest first. `n` has the same limits as `/historico`. `passo` is an integer from 1 to 60 that divides 60 (1, 5, 15, 30, 60, ...), otherwise `422`. `de` and `ate` limit the period like in `/estatisticas`.

```json
[{"minuto": "2026-11-06 12:54", "temperatura": 22.9, "humidade": 39.5}]
```

`minuto` is the start of the block (UTC). The newest entry is the block in progress, so its average is incomplete.

### `GET /live`

HTML page (`static/live.html`). It polls `/` and `/media` every second, `/historico?n=60` and `/estatisticas` every 5 s and `/medias` every 60 s. It shows the current values with the difference to the 15 min average and the min/max of the last hour, the last 60 readings, averages for 15 min, 1 h, 6 h or 24 h, a min/average/max table for 15 min to 7 days, and a day picker (last 7 days, in local time) with that day's statistics and 15 min averages. Static files are served from `/static`.

## Database

SQLite file `reads.db`, created on startup in the folder the server runs from. It is in `.gitignore`.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | Primary key |
| `temperatura` | REAL | Celsius |
| `humidade` | REAL | Percent |
| `hora` | TEXT | `CURRENT_TIMESTAMP`, UTC, `YYYY-MM-DD HH:MM:SS` |

Only valid readings are saved. Readings older than 7 days are deleted on startup and every 720 saves (about 1 h). `database.py` opens a new connection per call, because the reading thread and the request threads cannot share one SQLite connection by default.
