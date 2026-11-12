#include "server_commands.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Linux e macOS usam fork/kill/waitpid. O Windows usa CreateProcess/taskkill.
// A parte do Windows NAO foi testada num Windows a sério.
#ifdef _WIN32
    #include <windows.h>
    #define DEVNULL "NUL"
    #define UVICORN ".venv\\Scripts\\uvicorn.exe"
#else
    #include <fcntl.h>
    #include <signal.h>
    #include <sys/types.h>
    #include <sys/wait.h>
    #include <unistd.h>
    #define DEVNULL "/dev/null"
    #define UVICORN ".venv/bin/uvicorn"
#endif

#define PID_FILE "server.pid"
#define LOG_FILE "server.log"

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
static long read_pid(void)
{
    char path[512];
    pid_path(path, sizeof path);

    FILE *f = fopen(path, "r");
    if (f == NULL) { return -1; }

    long pid = -1;
    if (fscanf(f, "%ld", &pid) != 1) { pid = -1; }
    fclose(f);

    return pid > 0 ? pid : -1;
}

static void write_pid(long pid)
{
    char path[512];
    pid_path(path, sizeof path);

    FILE *f = fopen(path, "w");
    if (f != NULL) {
        fprintf(f, "%ld\n", pid);
        fclose(f);
    }
}

static void remove_pid(void)
{
    char path[512];

    pid_path(path, sizeof path);
    remove(path); // remove() e standard, funciona nos dois sistemas
}

static int run(const char *command)
{
    int status = system(command);

#ifdef _WIN32
    return status; // no Windows o system() ja devolve o codigo de saida
#else
    if (status == -1 || !WIFEXITED(status)) {
        return -1;
    }
    return WEXITSTATUS(status);
#endif
}

// ---------------------------------------------------------------------------
// A parte que depende do sistema: ver se o processo existe, parar, arrancar,
// ver se morreu e esperar.
// ---------------------------------------------------------------------------

#ifdef _WIN32

static int process_alive(long pid)
{
    HANDLE h = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, (DWORD)pid);
    if (h == NULL) {
        return 0;
    }

    DWORD code = 0;
    int alive = GetExitCodeProcess(h, &code) && code == STILL_ACTIVE;
    CloseHandle(h);
    return alive;
}

// taskkill /T mata tambem os processos filhos (o uvicorn pode lancar o python
// como filho). Nao tem o encerramento limpo do SIGTERM.
static int stop_process(long pid)
{
    char command[128];
    snprintf(command, sizeof command, "taskkill /PID %ld /T /F > " DEVNULL " 2>&1", pid);
    return run(command);
}

static int child_died(long pid)
{
    return !process_alive(pid);
}

static void sleep_ms(int ms)
{
    Sleep((DWORD)ms);
}

// devolve o PID do servidor, ou -1 se falhou
static long spawn_server(void)
{
    // handles herdaveis, para o filho escrever no log
    SECURITY_ATTRIBUTES sa;
    ZeroMemory(&sa, sizeof sa);
    sa.nLength = sizeof sa;
    sa.bInheritHandle = TRUE;

    char log_path[512];
    snprintf(log_path, sizeof log_path, "%s\\%s", project_root(), LOG_FILE);

    HANDLE log = CreateFileA(log_path, FILE_APPEND_DATA, FILE_SHARE_READ | FILE_SHARE_WRITE,
                             &sa, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    HANDLE nul = CreateFileA("NUL", GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE,
                             &sa, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (log == INVALID_HANDLE_VALUE || nul == INVALID_HANDLE_VALUE) {
        return -1;
    }

    STARTUPINFOA si;
    ZeroMemory(&si, sizeof si);
    si.cb = sizeof si;
    si.dwFlags = STARTF_USESTDHANDLES;
    si.hStdInput = nul;
    si.hStdOutput = log;
    si.hStdError = log;

    // caminho completo: o CreateProcess procura relativo a pasta do launcher,
    // e nao a pasta que damos em lpCurrentDirectory
    char command[512];
    snprintf(command, sizeof command, "\"%s\\%s\" server.main:app", project_root(), UVICORN);

    PROCESS_INFORMATION pi;
    ZeroMemory(&pi, sizeof pi);

    // DETACHED_PROCESS: sem consola, nao morre quando a do launcher fecha
    BOOL ok = CreateProcessA(NULL, command, NULL, NULL, TRUE,
                             DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                             NULL, project_root(), &si, &pi);

    CloseHandle(log);
    CloseHandle(nul);

    if (!ok) {
        return -1;
    }

    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    return (long)pi.dwProcessId;
}

#else

static int process_alive(long pid)
{
    // kill com o sinal 0 so verifica se o processo existe n envia nada
    return kill((pid_t)pid, 0) == 0;
}

static int stop_process(long pid)
{
    return kill((pid_t)pid, SIGTERM);
}

static int child_died(long pid)
{
    int status;
    return waitpid((pid_t)pid, &status, WNOHANG) == (pid_t)pid;
}

static void sleep_ms(int ms)
{
    usleep((useconds_t)ms * 1000);
}

// devolve o PID do servidor, ou -1 se o fork falhou
static long spawn_server(void)
{
    pid_t pid = fork();

    // fork devolve um valor negativo se nao conssegui criar o processo
    if (pid < 0) {
        return -1;
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
        int null = open(DEVNULL, O_RDONLY);

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
    return (long)pid;
}

#endif

// ---------------------------------------------------------------------------

int server_status(const char *option)
{
    if (option == NULL) {
        return -1;
    }

    if (strcmp(option, "process") == 0) {
        long pid = read_pid();
        return (pid > 0 && process_alive(pid)) ? 0 : 1;
    }

    if (strcmp(option, "http") == 0) {
        return run("curl -fs --max-time 2 http://127.0.0.1:8000/ > " DEVNULL " 2>&1");
    }

    // a pagina e um ficehiro estatico, responde logo que o servidor arranca
    if (strcmp(option, "live") == 0) {
        return run("curl -fs --max-time 2 http://127.0.0.1:8000/live > " DEVNULL " 2>&1");
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

    long pid = spawn_server();

    if (pid < 0) {
        puts("failed to create server process");
        return 1;
    }

    write_pid(pid);

    // espera ate ~5s ou o server responde ou o filho morre
    for (int i = 0; i < 25; i++) {
        if (child_died(pid)) {
            puts("server exited right after starting, see server.log");
            remove_pid();
            return 1;
        }

        if (server_status("live") == 0) {
            printf("server started (pid: %ld)\n", pid);
            return 0;
        }

        sleep_ms(200); // 0.2 s
    }

    puts("server did not answer in 5s, see server.log");
    return 1;
}

int server_stop(void)
{
    long pid = read_pid();

    if (pid < 0) {
        puts("server is not running (no pid file)");
        return 1;
    }

    if (stop_process(pid) != 0) {
        // o processo ja nao existe, o file era antigo
        if (!process_alive(pid)) {
            remove_pid();
        }
        puts("server failed to be killed");
        return 1;
    }

    remove_pid();
    puts("server stopped");
    return 0;
}
