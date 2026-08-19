/* Copyright 2026 Josh Kearney and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

#include "pyhole/hooks.h"
#include "pyhole/util.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static char g_sent[16][256];
static int g_nsent;

static void capture_send(Session *s, const char *target, const char *msg)
{
    (void)s;
    (void)target;
    if (g_nsent < 16) {
        snprintf(g_sent[g_nsent++], sizeof(g_sent[0]), "%s", msg);
    }
}

static void echo_cmd(Message *m, const char *params)
{
    message_dispatch(m, params ? params : "empty");
}

int main(void)
{
    hooks_reset();
    hook_add_command("echo", echo_cmd, "echo help");

    Session s;
    memset(&s, 0, sizeof(s));
    snprintf(s.nick, sizeof(s.nick), "pyhole");
    snprintf(s.command_prefix, sizeof(s.command_prefix), ".");
    s.admins = str_split_list("alice!ident");
    s.send_privmsg = capture_send;

    Message m = {.session = &s, .text = ".echo hello", .source = "alice!ident", .target = "#chan"};
    hooks_dispatch(&s, &m, false);
    int rc = 0;
    if (g_nsent != 1 || strcmp(g_sent[0], "hello") != 0) {
        fprintf(stderr, "command prefix: got '%s'\n", g_nsent ? g_sent[0] : "");
        rc = 1;
    }

    g_nsent = 0;
    m.text = "pyhole: echo hi";
    hooks_dispatch(&s, &m, false);
    if (g_nsent != 1 || strcmp(g_sent[0], "alice: hi") != 0) {
        fprintf(stderr, "addressed: got '%s'\n", g_nsent ? g_sent[0] : "");
        rc = 1;
    }

    g_nsent = 0;
    m.text = "echo secret";
    hooks_dispatch(&s, &m, true);
    if (g_nsent != 1 || strcmp(g_sent[0], "secret") != 0) {
        fprintf(stderr, "private: got '%s'\n", g_nsent ? g_sent[0] : "");
        rc = 1;
    }

    if (!hooks_is_admin(&s, "alice!ident") || hooks_is_admin(&s, "eve!ident")) {
        fprintf(stderr, "admin check\n");
        rc = 1;
    }

    hooks_reset();
    str_list_free(s.admins);
    if (rc == 0) {
        puts("test_hooks ok");
    }
    return rc;
}
