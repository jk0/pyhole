/* Copyright 2010-2026 Josh Kearney and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

#include "pyhole/util.h"

#include <ctype.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void *xmalloc(size_t n)
{
    void *p = malloc(n ? n : 1);
    if (p == NULL) {
        fprintf(stderr, "pyhole: out of memory\n");
        abort();
    }
    return p;
}

void *xcalloc(size_t n, size_t sz)
{
    void *p = calloc(n ? n : 1, sz ? sz : 1);
    if (p == NULL) {
        fprintf(stderr, "pyhole: out of memory\n");
        abort();
    }
    return p;
}

char *xstrdup(const char *s)
{
    if (s == NULL) {
        return NULL;
    }
    size_t n = strlen(s) + 1;
    char *p = xmalloc(n);
    memcpy(p, s, n);
    return p;
}

char *xstrndup(const char *s, size_t n)
{
    char *p = xmalloc(n + 1);
    memcpy(p, s, n);
    p[n] = '\0';
    return p;
}

char *str_trim(char *s)
{
    while (*s && isspace((unsigned char)*s)) {
        s++;
    }
    if (*s == '\0') {
        return s;
    }
    char *end = s + strlen(s) - 1;
    while (end > s && isspace((unsigned char)*end)) {
        *end-- = '\0';
    }
    return s;
}

bool str_eq_ci(const char *a, const char *b)
{
    if (a == NULL || b == NULL) {
        return a == b;
    }
    while (*a && *b) {
        if (tolower((unsigned char)*a) != tolower((unsigned char)*b)) {
            return false;
        }
        a++;
        b++;
    }
    return *a == *b;
}

bool str_starts(const char *s, const char *prefix)
{
    if (s == NULL || prefix == NULL) {
        return false;
    }
    return strncmp(s, prefix, strlen(prefix)) == 0;
}

bool str_starts_ci(const char *s, const char *prefix)
{
    if (s == NULL || prefix == NULL) {
        return false;
    }
    while (*prefix) {
        if (tolower((unsigned char)*s) != tolower((unsigned char)*prefix)) {
            return false;
        }
        s++;
        prefix++;
    }
    return true;
}

bool str_is_channel(const char *s)
{
    return s != NULL && (*s == '#' || *s == '&' || *s == '+' || *s == '!');
}

char **str_split_list(const char *s)
{
    size_t cap = 4, n = 0;
    char **out = xcalloc(cap, sizeof(*out));
    if (s == NULL || *s == '\0') {
        return out;
    }
    char *copy = xstrdup(s);
    char *p = copy;
    while (*p) {
        char *comma = strchr(p, ',');
        if (comma) {
            *comma = '\0';
        }
        char *item = str_trim(p);
        if (*item) {
            if (n + 1 >= cap) {
                cap *= 2;
                char **grown = xcalloc(cap, sizeof(*grown));
                memcpy(grown, out, n * sizeof(*out));
                free(out);
                out = grown;
            }
            out[n++] = xstrdup(item);
        }
        if (comma == NULL) {
            break;
        }
        p = comma + 1;
    }
    free(copy);
    return out;
}

void str_list_free(char **list)
{
    if (list == NULL) {
        return;
    }
    for (size_t i = 0; list[i]; i++) {
        free(list[i]);
    }
    free(list);
}

size_t str_list_len(char **list)
{
    size_t n = 0;
    if (list == NULL) {
        return 0;
    }
    while (list[n]) {
        n++;
    }
    return n;
}

bool str_list_contains(char **list, const char *item)
{
    if (list == NULL || item == NULL) {
        return false;
    }
    for (size_t i = 0; list[i]; i++) {
        if (strcmp(list[i], item) == 0) {
            return true;
        }
    }
    return false;
}

char *str_join(char **list, const char *sep)
{
    if (list == NULL || list[0] == NULL) {
        return xstrdup("");
    }
    size_t seplen = strlen(sep);
    size_t total = 0;
    size_t n = 0;
    for (; list[n]; n++) {
        total += strlen(list[n]);
        if (n > 0) {
            total += seplen;
        }
    }
    char *out = xmalloc(total + 1);
    out[0] = '\0';
    for (size_t i = 0; i < n; i++) {
        if (i > 0) {
            strcat(out, sep);
        }
        strcat(out, list[i]);
    }
    return out;
}

static void append_char(char **buf, size_t *len, size_t *cap, char c)
{
    if (*len + 1 >= *cap) {
        *cap *= 2;
        char *nbuf = xmalloc(*cap);
        memcpy(nbuf, *buf, *len);
        free(*buf);
        *buf = nbuf;
    }
    (*buf)[(*len)++] = c;
    (*buf)[*len] = '\0';
}

char *decode_entities(const char *html)
{
    size_t cap = 64, len = 0;
    char *out = xmalloc(cap);
    out[0] = '\0';
    bool in_tag = false;
    if (html == NULL) {
        return out;
    }
    for (const char *p = html; *p; p++) {
        if (*p == '<') {
            in_tag = true;
            continue;
        }
        if (*p == '>') {
            in_tag = false;
            continue;
        }
        if (in_tag) {
            continue;
        }
        if (*p == '&') {
            const char *end = strchr(p, ';');
            if (end && (size_t)(end - p) < 10) {
                char ent[12];
                size_t n = (size_t)(end - p + 1);
                memcpy(ent, p, n);
                ent[n] = '\0';
                char decoded = 0;
                if (strcmp(ent, "&amp;") == 0) {
                    decoded = '&';
                } else if (strcmp(ent, "&lt;") == 0) {
                    decoded = '<';
                } else if (strcmp(ent, "&gt;") == 0) {
                    decoded = '>';
                } else if (strcmp(ent, "&quot;") == 0) {
                    decoded = '"';
                } else if (strcmp(ent, "&#64;") == 0) {
                    decoded = '@';
                } else if (ent[1] == '#' && isdigit((unsigned char)ent[2])) {
                    decoded = (char)atoi(ent + 2);
                }
                if (decoded) {
                    if (decoded > 9 && decoded < 127) {
                        append_char(&out, &len, &cap, decoded);
                    }
                    p = end;
                    continue;
                }
            }
        }
        if ((unsigned char)*p > 9 && (unsigned char)*p < 127) {
            append_char(&out, &len, &cap, *p);
        }
    }
    return out;
}

bool ensure_int(const char *s, int *out)
{
    if (s == NULL) {
        return false;
    }
    char buf[64];
    size_t n = 0;
    for (const char *p = s; *p && n + 1 < sizeof(buf); p++) {
        if (isalnum((unsigned char)*p)) {
            buf[n++] = *p;
        }
    }
    buf[n] = '\0';
    if (n == 0) {
        return false;
    }
    char *end = NULL;
    long v = strtol(buf, &end, 10);
    if (end == buf || *end != '\0') {
        return false;
    }
    *out = (int)v;
    return true;
}

void pyhole_spawn(void *(*fn)(void *), void *arg)
{
    pthread_t thread;
    pthread_attr_t attr;
    pthread_attr_init(&attr);
    pthread_attr_setdetachstate(&attr, PTHREAD_CREATE_DETACHED);
    if (pthread_create(&thread, &attr, fn, arg) != 0) {
        fn(arg);
    }
    pthread_attr_destroy(&attr);
}
