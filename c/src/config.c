/* Copyright 2010-2026 Josh Kearney and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

#include "pyhole/config.h"

#include "pyhole/util.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct Entry {
    char *section;
    char *key;
    char *value;
    struct Entry *next;
} Entry;

struct Config {
    Entry *head;
};

Config *config_load(const char *path)
{
    FILE *fp = fopen(path, "r");
    if (fp == NULL) {
        return NULL;
    }
    Config *c = xcalloc(1, sizeof(*c));
    char line[1024];
    char section[128] = "";
    Entry *tail = NULL;
    while (fgets(line, sizeof(line), fp)) {
        char *nl = strchr(line, '\n');
        if (nl) {
            *nl = '\0';
        }
        char *cr = strchr(line, '\r');
        if (cr) {
            *cr = '\0';
        }
        char *s = str_trim(line);
        if (*s == '\0' || *s == '#' || *s == ';') {
            continue;
        }
        if (*s == '[') {
            char *end = strchr(s, ']');
            if (end == NULL) {
                continue;
            }
            *end = '\0';
            snprintf(section, sizeof(section), "%s", str_trim(s + 1));
            continue;
        }
        char *eq = strchr(s, '=');
        if (eq == NULL || section[0] == '\0') {
            continue;
        }
        *eq = '\0';
        char *key = str_trim(s);
        char *value = str_trim(eq + 1);
        Entry *e = xcalloc(1, sizeof(*e));
        e->section = xstrdup(section);
        e->key = xstrdup(key);
        e->value = xstrdup(value);
        if (tail) {
            tail->next = e;
        } else {
            c->head = e;
        }
        tail = e;
    }
    fclose(fp);
    return c;
}

void config_free(Config *c)
{
    if (c == NULL) {
        return;
    }
    Entry *e = c->head;
    while (e) {
        Entry *n = e->next;
        free(e->section);
        free(e->key);
        free(e->value);
        free(e);
        e = n;
    }
    free(c);
}

bool config_has_section(const Config *c, const char *section)
{
    if (c == NULL) {
        return false;
    }
    for (Entry *e = c->head; e; e = e->next) {
        if (strcmp(e->section, section) == 0) {
            return true;
        }
    }
    return false;
}

bool config_has_key(const Config *c, const char *section, const char *key)
{
    return config_get(c, section, key) != NULL;
}

const char *config_get(const Config *c, const char *section, const char *key)
{
    if (c == NULL) {
        return NULL;
    }
    for (Entry *e = c->head; e; e = e->next) {
        if (strcmp(e->section, section) == 0 && strcmp(e->key, key) == 0) {
            return e->value;
        }
    }
    return NULL;
}

const char *config_get_def(const Config *c, const char *section, const char *key, const char *def)
{
    const char *v = config_get(c, section, key);
    return v ? v : def;
}

int config_get_int(const Config *c, const char *section, const char *key, int def)
{
    const char *v = config_get(c, section, key);
    if (v == NULL || *v == '\0') {
        return def;
    }
    return atoi(v);
}

bool config_get_bool(const Config *c, const char *section, const char *key, bool def)
{
    const char *v = config_get(c, section, key);
    if (v == NULL || *v == '\0') {
        return def;
    }
    if (str_eq_ci(v, "true") || str_eq_ci(v, "yes") || strcmp(v, "1") == 0) {
        return true;
    }
    if (str_eq_ci(v, "false") || str_eq_ci(v, "no") || strcmp(v, "0") == 0) {
        return false;
    }
    return def;
}

char **config_get_list(const Config *c, const char *section, const char *key)
{
    return str_split_list(config_get_def(c, section, key, ""));
}
