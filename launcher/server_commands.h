#ifndef SERVER_COMMANDS_H
#define SERVER_COMMANDS_H

// Todas as funcoes devolvem 0 em sucesso e diferente de 0 em falha.

// option: "process", "http" ou "live". 0 = ligado, != 0 = desligado, -1 = opcao invalida.
int server_status(const char *option);
int server_start(void);
int server_stop(void);

#endif
