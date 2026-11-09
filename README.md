# intern_project

Um monitor simples de sensores de carro para o meu estágio: um Arduino lê os sensores, um pequeno servidor FastAPI guarda as leituras e mostra-as numa página web.

O objetivo é temperatura, humidade, CO2 e gás. Por agora só funcionam a temperatura e a humidade.

## Funcionalidades

- **Temperatura e humidade**: DHT22 no pino 2, lido de 5 em 5 s por `arduino/main/main.ino`
- **Página ao vivo**: `/live` mostra a leitura atual comparada com a média de 15 min, gráficos ao vivo, médias e estatísticas (mínimo, média e máximo) para vários períodos, e qualquer um dos últimos 7 dias em separado, com um botão de modo escuro que fica guardado
- **Histórico**: cada leitura válida é guardada em SQLite (`reads.db`, criada no arranque), por isso a média sobrevive a um reinício do servidor. As leituras com mais de 7 dias são apagadas
- **Volta a ligar sozinho**: se desligares o Arduino a página mostra um erro, e se o voltares a ligar recupera sem reiniciar
- **Rotas**: `/` última leitura em JSON (503 em caso de erro), `/media` média dos últimos 15 min (404 se não houver leituras), `/historico` as últimas N leituras, `/medias` médias em blocos de N minutos, `/estatisticas` mínimo, média e máximo (últimos N minutos ou um período fixo), `/live` a página

## Como correr

Precisas de um Arduino com o sketch de `arduino/main/main.ino` e um DHT22 no pino 2, ligado por USB. A porta série vem da variável de ambiente `PORTA_SERIE` (por defeito `/dev/ttyACM0`), por exemplo `PORTA_SERIE=/dev/ttyUSB0 uvicorn server.main:app`.

```bash
git clone "https://github.com/otzpt/intern_project" && cd intern_project
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn server.main:app
```

Depois abre `http://127.0.0.1:8000/live`.

## Testes

```bash
.venv/bin/python -m unittest -v
```

## Limitações

Por agora só temperatura e humidade, o CO2 e o gás ainda não estão feitos.

Não há autenticação: se o servidor ouvir em `0.0.0.0`, qualquer pessoa na rede pode ler os dados.

## Documentação

- [API e base de dados](docs/api.md)
- [Hardware e protocolo série](docs/hardware.md)
- [Roadmap](docs/roadmap.md)
- [Código de conduta](CODE_OF_CONDUCT.md)

## Licença

[MIT](LICENSE)
