# intern_project (estágio escolar)

Monitor de sensores: Arduino (DHT22) lê, servidor FastAPI guarda em SQLite e mostra numa página. Servidor e sensor pesam cerca de 50% da nota.

## Comandos
- Servidor: `./sensor start` (ou `.venv/bin/uvicorn server.main:app`), página em http://127.0.0.1:8000/live
- Testes: `.venv/bin/python -m unittest`
- Launcher em C: `cd launcher && make run` (corre a partir de `launcher/`)

## Estrutura
`server/` (rotas, base de dados, parsing, página em `static/`), `tests/`, `launcher/` (CLI em C, mais `prototype/` GTK e `prototype_2/` raylib), `arduino/`, `docs/` (pt-PT), `sensor` (script bash).

## Regras para o Claude
- Modo professor: ler primeiro, apontar o erro, não dar a solução; escrever código só se pedirem. Detalhes na secção 13 do `~/.claude/CLAUDE.md` e na memória deste projeto.
- O código é do utilizador. Não fazer commit nem push sem pedirem. Mensagens de commit: curtas, informais, com humor.
- Relatório de estágio: tem de haver pelo menos 1 commit por dia de trabalho. Opcional: 1 por tarefa ou ficheiro concluído. Ao fim da sessão, se ainda não houve commit hoje, lembrar o utilizador. O commit continua a ser dele, só se faz se pedir.
- Verificar correndo (compilador, pty, curl) e dizer o que foi observado e o que foi inferido.
- O utilizador acompanha o limite de uso: uma tarefa por sessão, pesquisas em modo normal, não ler ficheiros grandes inteiros.

## Contexto
Estado, decisões e pendentes estão em `.claude/handoff.md`. Ler no início de uma tarefa. Notas pessoais (privadas, fora do Git) em `.claude/personal.md`: ler só se o utilizador falar de como se sente.
