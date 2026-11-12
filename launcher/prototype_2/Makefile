# Launcher em raylib: make compila, make run corre, make clean apaga o binario.
# O clean nao apaga o compile_commands.json: sem ele o LSP volta a dar erros.
# make compile_commands.json gera o ficheiro que o LSP (clangd) usa para achar o raylib.
CC     = gcc
RAYLIB = $(HOME)/libs/raylib/src
# o raylib traz o GLFW (glfw3.h) dentro da propria pasta
# -isystem: os avisos de dentro do raygui.h nao aparecem (so os do teu codigo)
CFLAGS = -Wall -Wextra -g -I$(RAYLIB) -I$(RAYLIB)/external/glfw/include -isystem .
LIBS   = -L$(RAYLIB) -lraylib -lGL -lm -lpthread -ldl -lrt -lX11

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
	rm -f $(BIN)

.PHONY: run clean
