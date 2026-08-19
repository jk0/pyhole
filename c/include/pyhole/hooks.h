/* Copyright 2010-2026 Josh Kearney and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
#ifndef PYHOLE_HOOKS_H
#define PYHOLE_HOOKS_H

#include <stdbool.h>
#include <stddef.h>

typedef struct Session Session;
typedef struct Message Message;

struct Message {
    Session *session;
    char *text;
    char *source;
    char *target;
};

struct Session {
    char nick[64];
    char command_prefix[8];
    char **admins;
    bool addressed;
    char version[128];
    void *impl;
    void (*send_privmsg)(Session *s, const char *target, const char *msg);
    void (*send_notice)(Session *s, const char *target, const char *msg);
    void (*op_user)(Session *s, const char *params);
    void (*deop_user)(Session *s, const char *params);
    void (*set_nick)(Session *s, const char *nick);
    void (*join_channel)(Session *s, const char *params);
    void (*part_channel)(Session *s, const char *channel);
};

typedef void (*hook_fn)(Message *m, const char *arg);

void hooks_reset(void);
void hook_add_command(const char *name, hook_fn fn, const char *help);
void hook_add_keyword(const char *name, hook_fn fn, const char *help);
void hook_add_regex(const char *pattern, hook_fn fn, const char *help);

void hooks_dispatch(Session *s, Message *m, bool priv);

void message_dispatch(Message *m, const char *reply);
Message *message_dup(const Message *m);
void message_free(Message *m);

/* Run fn in a detached thread with a copy of the message. */
void hook_spawn(hook_fn fn, Message *m, const char *arg);

char *hooks_command_list(void);
char *hooks_keyword_list(void);
const char *hooks_command_help(const char *name);
bool hooks_is_admin(Session *s, const char *source);

void plugins_register(char **names);

#endif
