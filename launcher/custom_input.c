#include <stdio.h>
#include <string.h>
#include "custom_input.h"

void input_int(const char *prompt, int *val) {
    char buf[64];
    printf("%s", prompt);
    if (fgets(buf, sizeof(buf), stdin) != NULL) {
        if (sscanf(buf, "%d", val) != 1) {
            *val = -1;
        }
    }
}

void input_float(const char *prompt, float *val) {
    char buf[64];
    printf("%s", prompt);
    if (fgets(buf, sizeof(buf), stdin) != NULL) {
        if (sscanf(buf, "%f", val) != 1) {
            *val = 0.0f;
        }
    }
}

void input_double(const char *prompt, double *val) {
    char buf[64];
    printf("%s", prompt);
    if (fgets(buf, sizeof(buf), stdin) != NULL) {
        if (sscanf(buf, "%lf", val) != 1) {
            *val = 0.0;
        }
    }
}

void input_char(const char *prompt, char *val) {
    char buf[64];
    printf("%s", prompt);
    if (fgets(buf, sizeof(buf), stdin) != NULL) {
        *val = buf[0];
    }
}

void input_str(const char *prompt, char *buf, size_t size) {
    printf("%s", prompt);
    if (fgets(buf, (int)size, stdin) != NULL) {
        buf[strcspn(buf, "\n")] = '\0';
    }
}
