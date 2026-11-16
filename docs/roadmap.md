# Roadmap

Propostas, não compromissos. Cada item diz o que mudaria no código.

## Feito

- DHT22 num Arduino, uma linha por leitura pela porta série
- O servidor lê a porta, volta a ligar quando o cabo é desligado e guarda as leituras válidas em SQLite
- Rotas `/`, `/media`, `/estatisticas`, `/historico`, `/medias`, `/live`
- Página ao vivo com gráficos, médias, estatísticas, seletor de dia e modo escuro
- Leituras com mais de 7 dias apagadas, testes de `unittest`

## Próximos sensores (CO2, gás)

O formato da linha está fixo em dois números: `parse_linha` em `server/leitura.py` falha com `ValueError` se houver mais um campo, e a tabela `reads` só tem `temperatura` e `humidade`.

1. Escolher um formato de linha que possa crescer, por exemplo `temperatura=21.9,humidade=39.7,co2=612`.
2. Atualizar o parser em `server/leitura.py` e a tabela em `server/database.py` (a `reads.db` existente precisa de migração).
3. Acrescentar os novos campos a `/`, `/historico`, `/medias`, `/estatisticas` e a `docs/api.md`.
4. Acrescentar um gráfico por grandeza em `server/static/live.html` e uma entrada em `GRAFICOS_ATUAL` e `GRAFICOS_MEDIA` em `server/static/script.js`.

## Outros computadores (host)

- A porta série define-se com `PORTA_SERIE`. Nomes típicos: `/dev/ttyACM0` ou `/dev/ttyUSB0` em Linux, `COM3` e semelhantes em Windows, `/dev/cu.usbmodem*` em macOS. Não foi testado fora de Linux.
- Ler a porta pode exigir permissões para o teu utilizador em Linux.
- O `requirements.txt` fixa as versões instaladas na `.venv` original (Python 3.14). A versão mínima de Python que funciona é desconhecida, testa antes de usar uma mais antiga.

## Outras placas (ESP32, Nano, outras)

O protocolo não depende da placa: qualquer placa que escreva `temperatura,humidade` numa linha a 9600 baud funciona com o servidor tal como está.

- Os `9600` baud estão escritos no código em `server/main.py` (`serial.Serial(PORTA, 9600, ...)`) e em `arduino/main/main.ino`. Outro valor obriga a alterar os dois. Tornar isto uma variável de ambiente como `PORTA_SERIE` evitava editar o código.
- O sketch usa a biblioteca `DHT.h` e o pino 2. Outras placas podem usar outros números de pino.

## Mais do que um dispositivo

Hoje há uma porta, uma thread de leitura e uma tabela sem coluna de dispositivo. Para vários dispositivos:

1. Acrescentar uma coluna `dispositivo` a `reads`.
2. Arrancar uma thread de leitura por porta, cada uma com a sua entrada no estado partilhado `ultima`.
3. Acrescentar um filtro `?dispositivo=` às rotas e um seletor à página.

## Sem fios em vez de USB

Uma placa com Wi-Fi podia enviar cada leitura com um `POST` HTTP em vez de usar a porta série. Isso pede uma rota nova em `server/main.py` que valide o corpo do pedido, e uma decisão sobre autenticação, já que o servidor não tem nenhuma.
