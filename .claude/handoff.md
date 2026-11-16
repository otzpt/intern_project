# Handoff (estado em 2026-11-16)

## O que existe e funciona
- **Servidor** (`server/`): FastAPI + SQLite (`reads.db`). Rotas: `/`, `/media`, `/estatisticas` (minutos ou `de`/`ate` em ISO), `/historico`, `/medias` (com `passo`), `/live`. Leituras com mais de 7 dias são apagadas (arranque e a cada 720 gravações). Sensor: `PORTA_SERIE`, por defeito `/dev/ttyACM0`. A rota `/` devolve 503 enquanto o Arduino não deu leitura (o "http off" do launcher pode ser normal).
- **Página** `/live`: números atuais, gráficos SVG, estatísticas por período, seletor de dia (últimos 7 dias), tema escuro guardado. Verificado pelo utilizador a 2026-11-16 (dito por ele, não observado por mim): filtros e seletor de dia no browser, erro do DHT com o fio de dados desligado e retenção na `reads.db`.
- **Testes**: 12 a passar com `unittest` (`tests/test_database.py`, `tests/test_leitura.py`). Rotas: `tests/smoke_rotas.py`, 9 casos com `urllib` (timeout de 3 s, sai com código 1 se algum falhar), corre com `.venv/bin/python tests/smoke_rotas.py` e precisa do servidor ligado. O `unittest` não o apanha. `/`, `/media` e `/estatisticas` só dão 200 com leituras recentes do Arduino; o resto não depende dele.
- **Parsing** em `server/leitura.py` (`parse_linha`, `ErroSensor`).
- **Docs e README em pt-PT**. Script `sensor` (bash): `setup`, `start [--porta]`, `status`.
- **Launcher em C** (`launcher/`): `main.c` (menu), `server_commands.c/.h` (start/stop/status com PID em `server.pid` e log em `server.log` na raiz), `custom_input.c/.h` (fgets+sscanf; em fim de entrada devolve 0, que no menu é sair). Testado em Linux com um pseudo-terminal. Ramo `windows-launcher` (atual): versão com `#ifdef _WIN32` (CreateProcess/taskkill), **não testada**; precisa de MSYS2, curl.exe, `PORTA_SERIE=COM3`.
- `launcher/prototype/` (GTK) e `launcher/prototype_2/` (raylib+raygui). O `raygui.h` (terceiros, 300 KB, versão 5.1-dev) já não está no Git: está no `.gitignore` e o README diz onde o obter. Continua no disco e no histórico.

## Pendentes, por peso
1. **Smoke test, arestas por fechar** (pequeno): a gralha "servdor" e a mensagem de timeout repetida (linhas 36 e 41 de `tests/smoke_rotas.py`); o ramo `isinstance(e.reason, socket.timeout)` (timeout na ligação) nunca foi testado; o servidor desligado não foi testado de ponta a ponta. O `except TimeoutError` foi testado com um servidor que aceita e não responde. Alternativa mais completa, se for preciso: mover `init_db`, `apagar_antigas` e o arranque da thread para um `lifespan` em `server/main.py`, instalar `httpx` (não está no `.venv`) e usar `TestClient(main.app)` sem `with`.
2. Testar o ramo `windows-launcher` num Windows e fazer merge.
3. CO2/gás quando houver sensores (`docs/roadmap.md`; a `reads.db` precisa de migração).

## Exercícios de aprendizagem em curso
- `~/projects/random_stuff/main.c` (ncurses, `@` com `a d w s`): ordem `getch, erase, mov, desenhar, refresh`. Aprendido: o `getch` faz refresh implícito; o `@@` vinha do `mov` depois do desenho; o "não aparece" vinha de `y = 50` fora do ecrã. Regra: mudar uma coisa de cada vez.
- Recordação a treinar: os 3 valores do `fork`, `kill(pid, 0)`, porquê ponteiro em `objectGen`, `<` contra `<=`, arrays (deslocar o corpo da cobra), escrever de memória um venv.
- GrabGame (ncurses) e SnakeGame: a versão raylib do snake está só no outro computador.

## Decisões e porquê
- Python no servidor (não é limitado pelo CPU), C++ no Arduino, C no launcher. C só onde medir um gargalo.
- Launcher: ponderados GTK, raylib, tkinter e webview; ficou o CLI em C, que já faz start, stop e status. Não há CLI em Python. GUI parada. Protótipo em ncurses ponderado e descartado a 2026-11-16: custava uma refatoração de `server_commands.c` (14 chamadas de impressão) e uma dependência nova, sem ser preciso para a nota.
- Relatório de estágio: pelo menos 1 commit por dia de trabalho (regra em `.claude/CLAUDE.md`).
- Mercado (pesquisa de 2026-11-12, fontes: portais e agregadores): no Landing.jobs, 52 vagas em Portugal, nenhuma de C, C++, Rust ou embebidos, quase nenhuma júnior; vagas de C++ embebido existem noutros sítios (VW Group Services Lisboa, Devoteam Porto, Bosch Aveiro, Tekever, EID, CEiiA); Rust sobretudo médio/sénior e também pede C/C++.
- Horas (Hackatime, dito pelo utilizador): cerca de 106 h em 3 meses (53 Python, 38 C, 15 JS); este projeto só cerca de 11 h.

## Outros repositórios tocados
- `~/projects/CodeLearner`: `docs/learner-notes.md` e `docs/learner-examples/javascript/` (ramo `feat/libraries-manuals`).
- `~/claude-config`: secção 13 do `CLAUDE.md` e memória deste projeto, sincronizados.

## Armadilhas
- Sessões do Claude Code ficam na pasta do diretório onde arrancaram. Arrancar sempre em `school/intern`.
- `launcher/` tem de ser o diretório de trabalho do launcher (a raiz do projeto é `..`, ou `SENSOR_ROOT`).
- `reads.db-journal` aparece e desaparece a cada gravação: é normal.
- O servidor que o launcher arranca fica a correr em segundo plano (`server.pid`); parar pela opção 2 do launcher.
