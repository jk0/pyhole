/* Copyright 2010-2026 Josh Kearney and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
#ifndef PYHOLE_CONFIG_H
#define PYHOLE_CONFIG_H

#include <stdbool.h>

typedef struct Config Config;

Config *config_load(const char *path);
void config_free(Config *c);

bool config_has_section(const Config *c, const char *section);
bool config_has_key(const Config *c, const char *section, const char *key);

/* NULL if missing. Pointer is owned by Config. */
const char *config_get(const Config *c, const char *section, const char *key);
const char *config_get_def(const Config *c, const char *section, const char *key, const char *def);
int config_get_int(const Config *c, const char *section, const char *key, int def);
bool config_get_bool(const Config *c, const char *section, const char *key, bool def);

/* Caller frees with str_list_free. */
char **config_get_list(const Config *c, const char *section, const char *key);

#endif
