/* Copyright 2010-2026 Josh Kearney and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

#include "pyhole/hooks.h"

#include "pyhole/log.h"
#include "pyhole/util.h"

#include <ctype.h>
#include <regex.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char *name;
    hook_fn fn;
    char *help;
} NamedHook;

typedef struct {
    regex_t re;
    hook_fn fn;
    char *help;
    bool compiled;
} RegexHook;

static NamedHook *g_commands;
static size_t g_ncommands;
static NamedHook *g_keywords;
static size_t g_nkeywords;
static RegexHook *g_regexes;
static size_t g_nregexes;

void hooks_reset(void)
{
    for (size_t i = 0; i < g_ncommands; i++) {
        free(g_commands[i].name);
        free(g_commands[i].help);
    }
    free(g_commands);
    g_commands = NULL;
    g_ncommands = 0;
    for (size_t i = 0; i < g_nkeywords; i++) {
        free(g_keywords[i].name);
        free(g_keywords[i].help);
    }
    free(g_keywords);
    g_keywords = NULL;
    g_nkeywords = 0;
    for (size_t i = 0; i < g_nregexes; i++) {
        if (g_regexes[i].compiled) {
            regfree(&g_regexes[i].re);
        }
        free(g_regexes[i].help);
    }
    free(g_regexes);
    g_regexes = NULL;
    g_nregexes = 0;
}

static void add_named(NamedHook **arr, size_t *n, const char *name, hook_fn fn, const char *help)
{
    *arr = realloc(*arr, (*n + 1) * sizeof(**arr));
    if (*arr == NULL) {
        abort();
    }
    (*arr)[*n].name = xstrdup(name);
    (*arr)[*n].fn = fn;
    (*arr)[*n].help = help ? xstrdup(help) : NULL;
    (*n)++;
}

void hook_add_command(const char *name, hook_fn fn, const char *help)
{
    add_named(&g_commands, &g_ncommands, name, fn, help);
}

void hook_add_keyword(const char *name, hook_fn fn, const char *help)
{
    add_named(&g_keywords, &g_nkeywords, name, fn, help);
}

void hook_add_regex(const char *pattern, hook_fn fn, const char *help)
{
    g_regexes = realloc(g_regexes, (g_nregexes + 1) * sizeof(*g_regexes));
    if (g_regexes == NULL) {
        abort();
    }
    RegexHook *h = &g_regexes[g_nregexes];
    memset(h, 0, sizeof(*h));
    h->fn = fn;
    h->help = help ? xstrdup(help) : NULL;
    if (regcomp(&h->re, pattern, REG_EXTENDED | REG_ICASE) == 0) {
        h->compiled = true;
        g_nregexes++;
    } else {
        log_error("invalid regex: %s", pattern);
        free(h->help);
    }
}

Message *message_dup(const Message *m)
{
    Message *c = xcalloc(1, sizeof(*c));
    c->session = m->session;
    c->text = xstrdup(m->text);
    c->source = xstrdup(m->source);
    c->target = xstrdup(m->target);
    return c;
}

void message_free(Message *m)
{
    if (m == NULL) {
        return;
    }
    free(m->text);
    free(m->source);
    free(m->target);
    free(m);
}

typedef struct {
    hook_fn fn;
    Message *msg;
    char *arg;
} SpawnJob;

static void *spawn_main(void *arg)
{
    SpawnJob *j = arg;
    j->fn(j->msg, j->arg);
    message_free(j->msg);
    free(j->arg);
    free(j);
    return NULL;
}

void hook_spawn(hook_fn fn, Message *m, const char *arg)
{
    SpawnJob *j = xcalloc(1, sizeof(*j));
    j->fn = fn;
    j->msg = message_dup(m);
    j->arg = arg ? xstrdup(arg) : NULL;
    pyhole_spawn(spawn_main, j);
}

void message_dispatch(Message *m, const char *reply)
{
    if (m == NULL || reply == NULL || m->session == NULL || m->session->send_privmsg == NULL) {
        return;
    }
    char copy[4096];
    snprintf(copy, sizeof(copy), "%s", reply);
    char *save = NULL;
    int lines = 0;
    for (char *line = strtok_r(copy, "\n", &save); line; line = strtok_r(NULL, "\n", &save)) {
        if (++lines > 8) {
            m->session->send_privmsg(m->session, m->target, "...");
            break;
        }
        if (m->session->addressed) {
            char nick[64];
            snprintf(nick, sizeof(nick), "%s", m->source);
            char *bang = strchr(nick, '!');
            if (bang) {
                *bang = '\0';
            }
            char prefixed[512];
            snprintf(prefixed, sizeof(prefixed), "%s: %s", nick, line);
            m->session->send_privmsg(m->session, m->target, prefixed);
        } else {
            m->session->send_privmsg(m->session, m->target, line);
        }
    }
}

bool hooks_is_admin(Session *s, const char *source)
{
    return s != NULL && str_list_contains(s->admins, source);
}

static void run_commands(Session *s, Message *m, bool priv)
{
    const char *msg = m->text ? m->text : "";
    size_t pfx_len = strlen(s->command_prefix);
    for (size_t i = 0; i < g_ncommands; i++) {
        s->addressed = false;
        const char *cmd = g_commands[i].name;
        size_t clen = strlen(cmd);
        const char *rest = NULL;

        if (priv) {
            if (str_starts_ci(msg, cmd) && (msg[clen] == '\0' || isspace((unsigned char)msg[clen]))) {
                rest = msg + clen;
                while (*rest && isspace((unsigned char)*rest)) {
                    rest++;
                }
                g_commands[i].fn(m, *rest ? rest : NULL);
            }
        }

        const char *body = NULL;
        if (str_starts(msg, s->command_prefix)) {
            body = msg + pfx_len;
        } else {
            size_t nlen = strlen(s->nick);
            if (strlen(msg) > nlen && str_starts_ci(msg, s->nick) && msg[nlen] == ':') {
                body = msg + nlen + 1;
                while (*body && isspace((unsigned char)*body)) {
                    body++;
                }
                s->addressed = true;
            } else {
                continue;
            }
        }
        if (str_starts_ci(body, cmd) && (body[clen] == '\0' || isspace((unsigned char)body[clen]))) {
            rest = body + clen;
            while (*rest && isspace((unsigned char)*rest)) {
                rest++;
            }
            g_commands[i].fn(m, *rest ? rest : NULL);
        }
    }
}

static void run_keywords(Message *m)
{
    if (m->text == NULL) {
        return;
    }
    char *copy = xstrdup(m->text);
    char *save = NULL;
    for (char *word = strtok_r(copy, " ", &save); word; word = strtok_r(NULL, " ", &save)) {
        for (size_t i = 0; i < g_nkeywords; i++) {
            size_t klen = strlen(g_keywords[i].name);
            if (str_starts_ci(word, g_keywords[i].name) && word[klen] != '\0') {
                g_keywords[i].fn(m, word + klen);
            }
        }
    }
    free(copy);
}

static void run_regexes(Message *m)
{
    if (m->text == NULL) {
        return;
    }
    for (size_t i = 0; i < g_nregexes; i++) {
        if (!g_regexes[i].compiled) {
            continue;
        }
        regmatch_t match[2];
        if (regexec(&g_regexes[i].re, m->text, 2, match, 0) == 0) {
            size_t n = (size_t)(match[0].rm_eo - match[0].rm_so);
            char *captured = xstrndup(m->text + match[0].rm_so, n);
            g_regexes[i].fn(m, captured);
            free(captured);
        }
    }
}

void hooks_dispatch(Session *s, Message *m, bool priv)
{
    s->addressed = false;
    run_commands(s, m, priv);
    run_keywords(m);
    run_regexes(m);
}

static char *join_names(NamedHook *arr, size_t n)
{
    char **names = xcalloc(n + 1, sizeof(*names));
    for (size_t i = 0; i < n; i++) {
        names[i] = arr[i].name;
    }
    char *out = str_join(names, ", ");
    free(names);
    return out;
}

char *hooks_command_list(void)
{
    return join_names(g_commands, g_ncommands);
}

char *hooks_keyword_list(void)
{
    return join_names(g_keywords, g_nkeywords);
}

const char *hooks_command_help(const char *name)
{
    for (size_t i = 0; i < g_ncommands; i++) {
        if (str_eq_ci(g_commands[i].name, name)) {
            return g_commands[i].help;
        }
    }
    for (size_t i = 0; i < g_nkeywords; i++) {
        if (str_eq_ci(g_keywords[i].name, name)) {
            return g_keywords[i].help;
        }
    }
    return NULL;
}


