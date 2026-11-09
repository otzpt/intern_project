# API

Servidor: FastAPI, arranca com `uvicorn server.main:app` (por defeito em `http://127.0.0.1:8000`).

## Rotas

### `GET /`

Última leitura do Arduino.

```json
{"temperatura": 21.9, "humidade": 39.7}
```

Os erros devolvem `503` com `{"detail": "<mensagem>"}`. Mensagens em `server/main.py`:

| Mensagem | Significado |
|---|---|
| `a espera da primeira leitura...` | O servidor acabou de arrancar e ainda não leu nada |
| `arduino ligado, a espera da primeira leitura...` | A porta abriu e o Arduino está a reiniciar (cerca de 7 s) |
| `sem dados do Arduino ha 8 s` | A porta está aberta mas não chegou nenhuma linha em 8 s |
| `sensor DHT sem leitura valida` | O Arduino escreveu `Erro a ler o DHT` |
| `leitura invalida: '<linha>'` | A linha não é `temperatura,humidade` |
| `Arduino desligado. A tentar de novo... ` | Não foi possível abrir a porta, tenta outra vez de 2 em 2 s |
| `erro na base de dados: <erro>` | A leitura era válida mas não foi possível guardá-la |

### `GET /media`

Média das leituras guardadas nos últimos 15 minutos.

```json
{"temperatura": 21.9, "humidade": 39.7}
```

Devolve `404` com `{"detail": "sem leituras nos ultimos 15 min"}` quando a janela não tem leituras. A média só conta as leituras que existem, por isso logo a seguir ao arranque cobre menos de 15 minutos.

### `GET /estatisticas?minutos=60`

Mínimo, média e máximo das leituras guardadas. `minutos` é um inteiro de 1 a 10080 (por defeito 60): a janela termina agora. Em alternativa, `de` e `ate` escolhem um período fixo, como datas ISO 8601 (`2026-11-09T00:00:00Z`, sem fuso conta como UTC). `de` está incluído, `ate` está excluído, e `minutos` é ignorado quando `de` é dado. Qualquer valor inválido devolve `422`.

```json
{"leituras": 711, "temperatura": {"min": 19.7, "media": 20.1, "max": 20.9}, "humidade": {"min": 62.0, "media": 64.1, "max": 67.0}}
```

Devolve `404` com `{"detail": "sem leituras nos ultimos <minutos> min"}` (ou `"sem leituras nesse intervalo"` com `de`) quando o período não tem leituras.

### `GET /historico?n=60`

As últimas `n` leituras guardadas, da mais antiga para a mais nova. `n` é um inteiro de 1 a 1000 (por defeito 60), qualquer outro valor devolve `422`.

```json
[{"hora": "2026-11-06 12:54:13", "temperatura": 22.9, "humidade": 39.4}]
```

`hora` é UTC, `YYYY-MM-DD HH:MM:SS`. Devolve `[]` quando a tabela está vazia.

### `GET /medias?n=30&passo=1`

Médias em blocos de `passo` minutos, os últimos `n` blocos que têm leituras, do mais antigo para o mais novo. `n` tem os mesmos limites que em `/historico`. `passo` é um inteiro de 1 a 60 que divide 60 (1, 5, 15, 30, 60, ...), caso contrário devolve `422`. `de` e `ate` limitam o período como em `/estatisticas`.

```json
[{"minuto": "2026-11-06 12:54", "temperatura": 22.9, "humidade": 39.5}]
```

`minuto` é o início do bloco (UTC). A entrada mais recente é o bloco em curso, por isso a média ainda está incompleta.

### `GET /live`

Página HTML (`server/static/live.html`). Pede `/` e `/media` todos os segundos, `/historico?n=60` e `/estatisticas` de 5 em 5 s e `/medias` de 60 em 60 s. Mostra os valores atuais com a diferença para a média de 15 min e o mínimo e máximo da última hora, as últimas 60 leituras, médias de 15 min, 1 h, 6 h ou 24 h, uma tabela de mínimo, média e máximo de 15 min a 7 dias, e um seletor de dia (últimos 7 dias, em hora local) com as estatísticas desse dia e médias de 15 min. Os ficheiros estáticos são servidos em `/static`.

## Base de dados

Ficheiro SQLite `reads.db`, criado no arranque na pasta onde o servidor corre. Está no `.gitignore`.

| Coluna | Tipo | Notas |
|---|---|---|
| `id` | INTEGER | Chave primária |
| `temperatura` | REAL | Celsius |
| `humidade` | REAL | Percentagem |
| `hora` | TEXT | `CURRENT_TIMESTAMP`, UTC, `YYYY-MM-DD HH:MM:SS` |

Só se guardam leituras válidas. As leituras com mais de 7 dias são apagadas no arranque e a cada 720 gravações (cerca de 1 h). `server/database.py` abre uma ligação nova em cada chamada, porque a thread de leitura e as threads dos pedidos não podem partilhar uma ligação SQLite por defeito.
