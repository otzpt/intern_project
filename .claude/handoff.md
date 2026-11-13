# Handoff (estado em 2026-11-13)

## O que existe e funciona
- **Servidor** (`server/`): FastAPI + SQLite (`reads.db`). Rotas: `/`, `/media`, `/estatisticas` (minutos ou `de`/`ate` em ISO), `/historico`, `/medias` (com `passo`), `/live`. Leituras com mais de 7 dias são apagadas (arranque e a cada 720 gravações). Sensor: `PORTA_SERIE`, por defeito `/dev/ttyACM0`. A rota `/` devolve 503 enquanto o Arduino não deu leitura (o "http off" do launcher pode ser normal).
- **Página** `/live`: números atuais, gráficos SVG, estatísticas por período, seletor de dia (últimos 7 dias), tema escuro guardado.
- **Testes**: 12 a passar (`tests/test_database.py`, `tests/test_leitura.py`). Não há testes das rotas.
- **Parsing** em `server/leitura.py` (`parse_linha`, `ErroSensor`).
- **Docs e README em pt-PT**. Script `sensor` (bash): `setup`, `start [--porta]`, `status`.
- **Launcher em C** (`launcher/`): `main.c` (menu), `server_commands.c/.h` (start/stop/status com PID em `server.pid` e log em `server.log` na raiz), `custom_input.c/.h` (fgets+sscanf; em fim de entrada devolve 0, que no menu é sair). Testado em Linux com um pseudo-terminal. Ramo `windows-launcher` (atual): versão com `#ifdef _WIN32` (CreateProcess/taskkill), **não testada**; precisa de MSYS2, curl.exe, `PORTA_SERIE=COM3`.
- `launcher/prototype/` (GTK) e `launcher/prototype_2/` (raylib+raygui). O `raygui.h` (terceiros, 300 KB) está no Git; decisão pendente: tirar com `git rm --cached` e nota no README.

## Pendentes, por peso
1. **Testes das rotas.** Caminho primitivo escolhido: `tests/smoke_rotas.py` com `urllib` (stdlib), servidor a correr, pares (caminho, código esperado); já corri um esboço e os 8 casos passaram. Caminho completo: mover `init_db`, `apagar_antigas` e o arranque da thread para um `lifespan` em `server/main.py`, instalar `httpx` (não está no `.venv`), `TestClient(main.app)` sem `with`.
2. **Verificar no real** (só o utilizador pode): filtros e seletor de dia no browser, erro do DHT com o fio de dados desligado (`sensor DHT sem leitura valida`), retenção na `reads.db`.
3. Testar o ramo `windows-launcher` num Windows e fazer merge.
4. O utilizador quer escrever sozinho um CLI (start/stop/status) em Python (`subprocess`, `os.kill`, `urllib`); eu só digo o que deve fazer.
5. CO2/gás quando houver sensores (`docs/roadmap.md`; a `reads.db` precisa de migração).

## Exercícios de aprendizagem em curso
- `~/projects/random_stuff/main.c` (ncurses, `@` com `a d w s`): ordem `getch, erase, mov, desenhar, refresh`. Aprendido: o `getch` faz refresh implícito; o `@@` vinha do `mov` depois do desenho; o "não aparece" vinha de `y = 50` fora do ecrã. Regra: mudar uma coisa de cada vez.
- Recordação a treinar: os 3 valores do `fork`, `kill(pid, 0)`, porquê ponteiro em `objectGen`, `<` contra `<=`, arrays (deslocar o corpo da cobra), escrever de memória um venv.
- GrabGame (ncurses) e SnakeGame: a versão raylib do snake está só no outro computador.

## Decisões e porquê
- Python no servidor (não é limitado pelo CPU), C++ no Arduino, C no launcher. C só onde medir um gargalo.
- Launcher: ponderados GTK, raylib, tkinter e webview; ficou o CLI em C. GUI parada.
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
