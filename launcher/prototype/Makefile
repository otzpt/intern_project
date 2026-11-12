# Launcher GTK4: make compila, make run corre, make clean apaga o binario.
# make compile_commands.json gera o ficheiro que o LSP (clangd) usa para achar o GTK.
CC     = gcc
CFLAGS = -Wall -Wextra -g $(shell pkg-config --cflags gtk4)
LIBS   = $(shell pkg-config --libs gtk4)
# para pedidos HTTP mais tarde (precisa de libsoup3 instalada):
# CFLAGS += $(shell pkg-config --cflags libsoup-3.0)
# LIBS   += $(shell pkg-config --libs libsoup-3.0)

SRC = $(wildcard *.c)
BIN = launcher

$(BIN): $(SRC) compile_commands.json
	$(CC) $(CFLAGS) $(SRC) -o $(BIN) $(LIBS)

run: $(BIN)
	./$(BIN)

# o LSP nao le este Makefile: da-lhe as mesmas flags num formato que ele entende
compile_commands.json: Makefile
	printf '[{"directory":"$(CURDIR)","command":"$(CC) $(CFLAGS) -c main.c","file":"main.c"}]\n' > $@

clean:
	rm -f $(BIN) compile_commands.json

.PHONY: run clean
