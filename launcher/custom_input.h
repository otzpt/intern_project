#ifndef INPUT_H
#define INPUT_H

#include <stddef.h>

// Internal functions for each data type
void input_int(const char *prompt, int *val);
void input_float(const char *prompt, float *val);
void input_double(const char *prompt, double *val);
void input_char(const char *prompt, char *val);
void input_str(const char *prompt, char *buf, size_t size);

// Helper macro to route 2-argument calls by pointer type
#define _INPUT_2(prompt, ptr) _Generic((ptr), \
    int *:    input_int,    \
    float *:  input_float,  \
    double *: input_double, \
    char *:   input_char    \
)(prompt, ptr)

// Helper macro to select between 2 arguments (numbers/char) and 3 arguments (strings)
#define _GET_INPUT_MACRO(_1, _2, _3, NAME, ...) NAME
#define input(...) _GET_INPUT_MACRO(__VA_ARGS__, input_str, _INPUT_2)(__VA_ARGS__)

#endif
