# make       compila o launcher
# make run   compila e corre (corre a partir desta pasta: o SENSOR_ROOT por defeito e "..")
# make clean apaga o binario e os ficheiros gerados
#
# Windows (NAO testado): precisa do MSYS2/MinGW (gcc e make) e do curl.exe.
# Defina PORTA_SERIE com a porta do Arduino (por exemplo COM3) antes de correr,
# e o venv tem de ter sido criado em .venv (o launcher usa .venv\Scripts\uvicorn.exe).
CC     = gcc
CFLAGS = -Wall -Wextra -Wshadow -g

SRC = $(wildcard *.c)
OBJ = $(SRC:.c=.o)
BIN = launcher

$(BIN): $(OBJ)
	$(CC) $(OBJ) -o $@

# -MMD -MP: o gcc escreve um .d com os .h de cada .c, para o make recompilar
# o .c quando um .h muda
%.o: %.c
	$(CC) $(CFLAGS) -MMD -MP -c $< -o $@

-include $(OBJ:.o=.d)

run: $(BIN)
	./$(BIN)

clean:
	rm -f $(BIN) $(OBJ) $(OBJ:.o=.d)

.PHONY: run clean
