#include <stdio.h>

#include "server_commands.h"
#include "custom_input.h"


void menu()
{
    puts("");
    puts("========================");
    puts("    SERVER LAUNCHER");
    puts("========================");
    puts(" [1] start server");
    puts(" [2] stop server");
    puts(" [3] server status");
    puts(" [0] exit");
    puts("========================");
}

void menu_status_server()
{
    puts("");
    puts("========================");
    puts("     SERVER STATUS");
    puts("========================");
    puts(" [1] all");
    puts(" [2] process");
    puts(" [3] http");
    puts(" [4] live");
    puts(" [0] back");
    puts("========================");
}

void wait_enter(int *pressed_key)
{
    *pressed_key = getchar();
    while (*pressed_key != '\n' && *pressed_key != EOF) {
        *pressed_key = getchar();
    }
}

int main(void) {
    int option;
    int pressed_key = ' ';

    while(1) {
        menu();
        input("Enter the option you want to use: ", &option);

        if (option == 1) {
            // a funcao ja escreve a sua propria mensagem
            server_start();
            // dar tempo para o user ler
            puts("press enter to continue...");
            wait_enter(&pressed_key);
        } else if (option == 2) {
            server_stop();
            // dar tempo para o user ler
            puts("press enter to continue...");
            wait_enter(&pressed_key);
        } else if (option == 3){
            menu_status_server();
            input("Enter the option you want to use: ", &option);

            if (option == 1) {
                int result = server_status("process");
                int result2 = server_status("http");
                int result3 =server_status("live");

                // 0 = ligado, diferente de 0 = desligado (ver server_commands.h)
                printf("process: %s\n", result == 0 ? "on" : "off");
                printf("http:    %s\n", result2 == 0 ? "on" : "off");
                printf("live:    %s\n", result3 == 0 ? "on" : "off");
                // dar tempo para o user ler
                puts("press enter to continue...");
                wait_enter(&pressed_key);
            } else if (option == 2) {
                int result = server_status("process");
                printf("process: %s\n", result == 0 ? "on" : "off");
                // dar tempo para o user ler
                puts("press enter to continue...");
                wait_enter(&pressed_key);
            } else if (option == 3) {
                int result = server_status("http");
                printf("http:    %s\n", result == 0 ? "on" : "off");
                // dar tempo para o user ler
                puts("press enter to continue...");
                wait_enter(&pressed_key);
            } else if (option == 4) {
                int result = server_status("live");
                printf("live:    %s\n", result == 0 ? "on" : "off");
                // dar tempo para o user ler
                puts("press enter to continue...");
                wait_enter(&pressed_key);
            } else if (option == 0) {
                continue;
            } else {
                puts("invalid option");
            }
        } else if (option == 0) {
            puts("exiting");
            break;
        } else {
            puts("invalid option");
        }
    }

    return 0;
}
