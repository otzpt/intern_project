# make       compila o launcher
# make run   compila e corre (corre a partir desta pasta: o SENSOR_ROOT por defeito e "..")
# make clean apaga o binario e os ficheiros gerados
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
