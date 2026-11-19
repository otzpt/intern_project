# Handoff (estado em 2026-11-19)

## O que existe e funciona
- **Servidor** (`server/`): FastAPI + SQLite (`reads.db`). Rotas: `/`, `/media`, `/estatisticas` (minutos ou `de`/`ate` em ISO), `/historico`, `/medias` (com `passo`), `/estado` (leituras guardadas, primeira e última, retenção, porta e estado do Arduino; responde sempre 200), `/live`. Leituras com mais de 7 dias são apagadas (arranque e a cada 720 gravações; `RETENCAO_DIAS` em `server/main.py`). Sensor: `PORTA_SERIE`, por defeito `/dev/ttyACM0`. A rota `/` devolve 503 enquanto o Arduino não deu leitura (o "http off" do launcher pode ser normal).
- **Página** `/live` (redesenhada a 2026-11-18): barra lateral com 4 secções por `#` (Ao vivo, Estatísticas, Dia, Sistema), painéis com borda fina, tema claro/escuro com ícone, layout adaptado a ecrãs estreitos. Estatísticas junta o antigo seletor de período e as médias. Sem gradientes nem emojis, só fontes do sistema (funciona offline). Vista por mim no Firefox headless a 1280 px (claro e escuro) e 420 px com dados simulados; não vi o Sistema em modo claro nem o Dia em modo escuro. Secção Sistema atualiza de 5 em 5 s. Verificado pelo utilizador a 2026-11-16 (dito por ele): filtros, seletor de dia, erro do DHT com o fio desligado e retenção na `reads.db`.
- **Testes**: 25 a passar com `unittest` (`tests/test_database.py`, `tests/test_leitura.py`, `tests/test_rotas.py`; este usa `TestClient` com base temporária e não precisa de servidor nem de Arduino). Rotas: `tests/smoke_rotas.py`, 10 casos com `urllib` (timeout de 3 s, sai com código 1 se algum falhar), corre com `.venv/bin/python tests/smoke_rotas.py` e precisa do servidor ligado. O `unittest` não o apanha. `/`, `/media` e `/estatisticas` só dão 200 com leituras recentes do Arduino; o resto não depende dele. Os caminhos de erro (servidor desligado, ligação aceite sem resposta, timeout de ligação) foram simulados a 2026-11-16 com sockets locais: dão `FALHOU` e código 1. O `server/main.py` tem um `lifespan` (2026-11-18): `init_db`, `apagar_antigas` e a thread de leitura arrancam aí, por isso importar o `main` não tem efeitos. O `TestClient` é usado sem `with` para não o correr. `httpx` está no `requirements.txt`, numa secção só para testes. Aviso do Starlette: prefere `httpx2` (não mudei).
- **Arduino**: a 2026-11-18 a placa tinha código de outro sensor (uma linha com um só valor, o servidor rejeitava); foi regravada com `arduino/main/main.ino` e `/estado` passou a `a receber leituras`. `tests/smoke_rotas.py` deu 10/10 a 2026-11-19.
- **Simulador do Arduino** (`tests/simulador.py`, 2026-11-18): porta série virtual com `pty`, leituras aleatórias de 5 em 5 s e 1 em 10 de erro. Testado com o servidor real (leituras guardadas, erro no painel, parar dá "Arduino desligado"). Escrito pelo utilizador. As leituras falsas ficam na `reads.db` (saem em 7 dias).
- **Parsing** em `server/leitura.py` (`parse_linha`, `ErroSensor`).
- **Docs e README em pt-PT**. Script `sensor` (bash): `setup`, `start [--porta]`, `status`.
- **Launcher em C** (`launcher/`): `main.c` (menu), `server_commands.c/.h` (start/stop/status com PID em `server.pid` e log em `server.log` na raiz), `custom_input.c/.h` (fgets+sscanf; em fim de entrada devolve 0, que no menu é sair). Testado em Linux com um pseudo-terminal. Código para Windows (merge no `main` feito a 2026-11-16): versão com `#ifdef _WIN32` (CreateProcess/taskkill), **não testada**; precisa de MSYS2, curl.exe, `PORTA_SERIE=COM3`.
- `launcher/prototype/` (GTK) e `launcher/prototype_2/` (raylib+raygui). O `raygui.h` (terceiros, 300 KB, versão 5.1-dev) já não está no Git: está no `.gitignore` e o README diz onde o obter. Continua no disco e no histórico.

## Pendentes, por peso
1. Testar o launcher num Windows. O código já está no `main`. O ramo `windows-launcher` (local e remoto) está contido no `main` e pode ser apagado (`git branch -D windows-launcher` e `git push origin --delete windows-launcher`).
2. CO2/gás quando houver sensores (`docs/roadmap.md`; a `reads.db` precisa de migração).

## Ideia em desenho: IA no projeto (2026-11-19, so conversa, nada implementado)
- Modelo 1, decisor pequeno (~0,8M ou menos, scikit-learn ou PyTorch CPU): classifica a leitura (`normal`, `ruido`, `pico`, `preso`, `deriva`, `erro`). Treina no portatil. Rota `/analise` no servidor; comeca como regra estatistica e troca-se por modelo sem mudar a rota.
- Modelo 2, texto: `voidseed` (155M, ja no Ollama; ~282 tok/s medido no portatil) afinado para escrever a frase a partir do veredito e dos numeros. Treina em casa (2080 Super, 8 GB; fp16 com GradScaler, Turing sem bf16). Por confirmar: lingua das frases e tokenizador (TinyStories e ingles).
- Validacao por codigo: os numeros da frase tem de bater com os do veredito, senao usa-se uma frase feita por codigo. Regra e modelo 1 a discordar da `incerto`. Um modelo 3 so se o `incerto` aparecer muito.
- Simulador com modos (`normal`, `ruido`, `pico`, `deriva`, `preso`) da dados etiquetados para treinar e medir. Apontar a outra base de dados nos ensaios (por ver em `server/database.py`).
- Site: abas Analise, Ruido, Distribuicao, Eventos. O chat e opcional (Ollama no portatil).
- Hardware: portatil RTX 3050 4 GB corre tudo menos o treino do modelo 2. O Pi 3B (1 GB) so serviria para o decisor, nao para o texto.

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
