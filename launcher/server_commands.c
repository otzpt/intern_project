#include "server_commands.h"

#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

#define PID_FILE "server.pid"
#define LOG_FILE "server.log"
#define UVICORN ".venv/bin/uvicorn"

// raiz do projeto, relatiac apasta do launcher
// ou o que estiver em sensor_root
static const char *project_root(void)
{
    const char *root = getenv("SENSOR_ROOT");

    return root ? root : "..";
}

static void pid_path(char *buf, size_t size)
{
    snprintf(buf, size, "%s/%s", project_root(), PID_FILE);
}

// -1 se n houver files ou conteudo nao e um pid
static pid_t read_pid(void)
{
    char path[512];
    pid_path(path, sizeof path);

    FILE *f = fopen(path, "r");
    if (f == NULL) { return -1; }

    long pid = -1;
    if (fscanf(f, "%ld", &pid) != 1) { pid = -1; }
    fclose(f);

    return pid > 0 ? (pid_t)pid : -1;
}

static void write_pid(pid_t pid)
{
    char path[512];
    pid_path(path, sizeof path);

    FILE *f = fopen(path, "w");
    if (f != NULL) {
        fprintf(f, "%ld\n", (long)pid);
        fclose(f);
    }
}

static void remove_pid(void)
{
    char path[512];

    pid_path(path, sizeof path);
    unlink(path);
}

static int run(const char *command)
{
    int status = system(command);

    if (status == -1 || !WIFEXITED(status)) {
        return -1;
    }
    return WEXITSTATUS(status);
}

int server_status(const char *option)
{
    if (option == NULL) {
        return -1;
    }

    if (strcmp(option, "process") == 0) {
        // kill com o sinal 0 so verifica se o processo existe n envia nada
        pid_t pid = read_pid();
        return (pid > 0 && kill(pid, 0) == 0) ? 0 : 1;
    }

    if (strcmp(option, "http") == 0) {
        return run("curl -fs --max-time 2 http://127.0.0.1:8000/ > /dev/null 2>&1");
    }

    // a pagina e um ficehiro estatico, responde logo que o servidor arranca
    if (strcmp(option, "live") == 0) {
        return run("curl -fs --max-time 2 http://127.0.0.1:8000/live > /dev/null 2>&1");
    }

    return -1;
}

int server_start(void)
{
    if (server_status("live") == 0) {
        puts("server is already running");
        return 0;
    }

    if (server_status("process") == 0) {
        puts("process exists but the server does not answer, use server_status to investigate");
        return 1;
    }

    pid_t pid = fork();

    // fork devolve um valor negativo se nao conssegui criar o processo
    if (pid < 0) {
        puts("failed to create server process");
        return 1;
    }

    // pid = 0; filho process
    if (pid == 0) {
        // nova sessao; o servidor deixa de morrer quando o terminal feixa
        setsid();

        // uvicorn so importa server.main se correr na raiz do projeto
        if (chdir(project_root()) != 0) {
            _exit(126);
        }

        // sem terminal a saido do server vai para um file
        int log = open(LOG_FILE, O_WRONLY | O_CREAT | O_APPEND, 0644);
        int null = open("/dev/null", O_RDONLY);

        if (log < 0 || null < 0) {
            _exit(126);
        }
        dup2(null, STDIN_FILENO);
        dup2(log, STDOUT_FILENO);
        dup2(log, STDERR_FILENO);

        // o ultimo elemento tem de ser NULL
        // sem --reload isso para desenvoler e cria processos extra; aka bloat
        char *args[] = {"uvicorn", "server.main:app", NULL};

        // o caminho e comple, execv nao procura path
        execv(UVICORN, args);

        // so chega aqui se o execv falhar
        _exit(127);
    }

    // pid > 0; processo pai
    write_pid(pid);

    // espera ate ~5s ou o server responde ou o filho morre
    for (int i = 0; i < 25; i++) {
        int status;
        if (waitpid(pid, &status, WNOHANG) == pid) {
            puts("server exited right after starting, see server.log");
            remove_pid();
            return 1;
        }

        if (server_status("live") == 0) {
            printf("server started (pid: %ld)\n", (long)pid);
            return 0;
        }

        usleep(200000); // 0.2 s
    }

    puts("server did not answer in 5s, see server.log");
    return 1;
}

int server_stop(void)
{
    pid_t pid = read_pid();

    if (pid < 0) {
        puts("server is not running (no pid file)");
        return 1;
    }

    if (kill(pid, SIGTERM) != 0) {
        // ESRCH: o processo ja nao existe, o file era antigo
        if (errno == ESRCH) {
            remove_pid();
        }
        puts("server failed to be killed");
        return 1;
    }

    remove_pid();
    puts("server stopped");
    return 0;
}
