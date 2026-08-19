/* Copyright 2010-2026 Josh Kearney and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
#ifndef PYHOLE_UTIL_H
#define PYHOLE_UTIL_H

#include <stdbool.h>
#include <stddef.h>

void *xmalloc(size_t n);
void *xcalloc(size_t n, size_t sz);
char *xstrdup(const char *s);
char *xstrndup(const char *s, size_t n);

char *str_trim(char *s);
bool str_eq_ci(const char *a, const char *b);
bool str_starts(const char *s, const char *prefix);
bool str_starts_ci(const char *s, const char *prefix);
bool str_is_channel(const char *s);

/* Comma-separated list; returns a NULL-terminated array. */
char **str_split_list(const char *s);
void str_list_free(char **list);
size_t str_list_len(char **list);
bool str_list_contains(char **list, const char *item);

char *str_join(char **list, const char *sep);

/* Strip tags and a handful of HTML entities; keep printable ASCII. */
char *decode_entities(const char *html);

/* Strip non-word characters and parse an int. Returns true on success. */
bool ensure_int(const char *s, int *out);

typedef void *(*spawn_fn)(void *);
/* Detached thread. `arg` ownership transfers to `fn`. */
void pyhole_spawn(void *(*fn)(void *), void *arg);

#endif
