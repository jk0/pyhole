/* Copyright 2010-2026 Josh Kearney and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

#include "pyhole/hooks.h"
#include "pyhole/util.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void cmd_help(Message *m, const char *params)
{
    if (params && *params) {
        const char *doc = hooks_command_help(params);
        if (doc) {
            message_dispatch(m, doc);
        } else {
            char buf[128];
            snprintf(buf, sizeof(buf), "No help available: %s", params);
            message_dispatch(m, buf);
        }
        return;
    }
    message_dispatch(m, "Learn how to use plugins (ex: .help <command>).");
    char *cmds = hooks_command_list();
    char *kws = hooks_keyword_list();
    if (cmds && cmds[0]) {
        char buf[512];
        snprintf(buf, sizeof(buf), "Active Commands: %s", cmds);
        message_dispatch(m, buf);
    }
    if (kws && kws[0]) {
        char buf[512];
        snprintf(buf, sizeof(buf), "Active Keywords: %s", kws);
        message_dispatch(m, buf);
    }
    free(cmds);
    free(kws);
}

static void cmd_version(Message *m, const char *params)
{
    (void)params;
    message_dispatch(m, m->session->version);
}

static void require_admin(Message *m, hook_fn fn, const char *params)
{
    if (!hooks_is_admin(m->session, m->source)) {
        message_dispatch(m, "Sorry, you are not authorized to do that.");
        return;
    }
    fn(m, params);
}

static void cmd_op(Message *m, const char *params)
{
    if (!params) {
        message_dispatch(m, "Op a user (ex: .op <channel> <nick>).");
        return;
    }
    if (m->session->op_user) {
        m->session->op_user(m->session, params);
    }
}

static void cmd_deop(Message *m, const char *params)
{
    if (!params) {
        message_dispatch(m, "De-op a user (ex: .deop <channel> <nick>).");
        return;
    }
    if (m->session->deop_user) {
        m->session->deop_user(m->session, params);
    }
}

static void cmd_nick(Message *m, const char *params)
{
    if (!params) {
        message_dispatch(m, "Change nick (ex: .nick <nick>).");
        return;
    }
    if (m->session->set_nick) {
        m->session->set_nick(m->session, params);
    }
}

static void cmd_join(Message *m, const char *params)
{
    if (!params) {
        message_dispatch(m, "Join a channel (ex: .join #channel [<key>]).");
        return;
    }
    if (m->session->join_channel) {
        m->session->join_channel(m->session, params);
    }
}

static void cmd_part(Message *m, const char *params)
{
    if (!params) {
        message_dispatch(m, "Part a channel (ex: .part <channel>).");
        return;
    }
    if (m->session->part_channel) {
        m->session->part_channel(m->session, params);
    }
}

static void cmd_say(Message *m, const char *params)
{
    if (!params) {
        message_dispatch(m, "Send a reply (ex: .say <channel>|<nick> message).");
        return;
    }
    const char *space = strchr(params, ' ');
    if (space == NULL) {
        message_dispatch(m, "Send a reply (ex: .say <channel>|<nick> message).");
        return;
    }
    char target[128];
    size_t n = (size_t)(space - params);
    if (n >= sizeof(target)) {
        n = sizeof(target) - 1;
    }
    memcpy(target, params, n);
    target[n] = '\0';
    if (m->session->send_privmsg) {
        m->session->send_privmsg(m->session, target, space + 1);
    }
}

static void admin_op(Message *m, const char *params)
{
    require_admin(m, cmd_op, params);
}
static void admin_deop(Message *m, const char *params)
{
    require_admin(m, cmd_deop, params);
}
static void admin_nick(Message *m, const char *params)
{
    require_admin(m, cmd_nick, params);
}
static void admin_join(Message *m, const char *params)
{
    require_admin(m, cmd_join, params);
}
static void admin_part(Message *m, const char *params)
{
    require_admin(m, cmd_part, params);
}
static void admin_say(Message *m, const char *params)
{
    require_admin(m, cmd_say, params);
}

void plugin_admin_register(void)
{
    hook_add_command("help", cmd_help, "Learn how to use plugins (ex: .help <command>).");
    hook_add_command("version", cmd_version, "Display the current version.");
    hook_add_command("op", admin_op, "Op a user (ex: .op <channel> <nick>).");
    hook_add_command("deop", admin_deop, "De-op a user (ex: .deop <channel> <nick>).");
    hook_add_command("nick", admin_nick, "Change nick (ex: .nick <nick>).");
    hook_add_command("join", admin_join, "Join a channel (ex: .join #channel [<key>]).");
    hook_add_command("part", admin_part, "Part a channel (ex: .part <channel>).");
    hook_add_command("say", admin_say, "Send a reply (ex: .say <channel>|<nick> message).");
}
