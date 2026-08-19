/* Copyright 2010-2026 Josh Kearney and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

#include "pyhole/irc.h"

#include "pyhole/log.h"
#include "pyhole/util.h"
#include "pyhole/version.h"

#include <errno.h>
#include <netdb.h>
#include <stdarg.h>
#include <time.h>
#include <openssl/err.h>
#include <openssl/ssl.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/select.h>
#include <sys/socket.h>
#include <unistd.h>

typedef struct {
    int fd;
    SSL *ssl;
    SSL_CTX *ctx;
    pthread_mutex_t wlock;
    char readbuf[8192];
    size_t readlen;
    char *password;
    char *username;
    char *identify;
    char **channels;
    char server[256];
    int port;
    bool use_ssl;
    bool ssl_verify;
    int reconnect_delay;
    int rejoin_delay;
} IrcImpl;

static int raw_write(IrcImpl *impl, const char *buf, size_t n)
{
    if (impl->ssl) {
        int rc = SSL_write(impl->ssl, buf, (int)n);
        return rc > 0 ? 0 : -1;
    }
    size_t off = 0;
    while (off < n) {
        ssize_t rc = send(impl->fd, buf + off, n - off, 0);
        if (rc < 0) {
            if (errno == EINTR) {
                continue;
            }
            return -1;
        }
        off += (size_t)rc;
    }
    return 0;
}

static int irc_printf(Session *s, const char *fmt, ...)
{
    IrcImpl *impl = s->impl;
    char buf[510];
    va_list ap;
    va_start(ap, fmt);
    int n = vsnprintf(buf, sizeof(buf), fmt, ap);
    va_end(ap);
    if (n < 0) {
        return -1;
    }
    if (n > (int)sizeof(buf) - 1) {
        n = (int)sizeof(buf) - 1;
    }
    buf[n++] = '\r';
    buf[n++] = '\n';
    pthread_mutex_lock(&impl->wlock);
    int rc = raw_write(impl, buf, (size_t)n);
    pthread_mutex_unlock(&impl->wlock);
    return rc;
}

static void send_privmsg(Session *s, const char *target, const char *msg)
{
    irc_printf(s, "PRIVMSG %s :%s", target, msg);
    if (str_is_channel(target)) {
        log_info("-%s- <%s> %s", target, s->nick, msg);
    } else {
        log_info("<%s> %s", s->nick, msg);
    }
}

static void send_notice(Session *s, const char *target, const char *msg)
{
    irc_printf(s, "NOTICE %s :%s", target, msg);
}

static void op_user(Session *s, const char *params)
{
    char buf[256];
    snprintf(buf, sizeof(buf), "%s", params ? params : "");
    char *space = strchr(buf, ' ');
    if (space == NULL) {
        return;
    }
    *space = '\0';
    irc_printf(s, "MODE %s +o %s", buf, space + 1);
}

static void deop_user(Session *s, const char *params)
{
    char buf[256];
    snprintf(buf, sizeof(buf), "%s", params ? params : "");
    char *space = strchr(buf, ' ');
    if (space == NULL) {
        return;
    }
    *space = '\0';
    irc_printf(s, "MODE %s -o %s", buf, space + 1);
}

static void set_nick(Session *s, const char *nick)
{
    snprintf(s->nick, sizeof(s->nick), "%s", nick);
    irc_printf(s, "NICK %s", nick);
}

static void join_channel(Session *s, const char *params)
{
    irc_printf(s, "JOIN %s", params);
}

static void part_channel(Session *s, const char *channel)
{
    irc_printf(s, "PART %s", channel);
}

static void irc_close(IrcImpl *impl)
{
    if (impl->ssl) {
        SSL_shutdown(impl->ssl);
        SSL_free(impl->ssl);
        impl->ssl = NULL;
    }
    if (impl->ctx) {
        SSL_CTX_free(impl->ctx);
        impl->ctx = NULL;
    }
    if (impl->fd >= 0) {
        close(impl->fd);
        impl->fd = -1;
    }
    impl->readlen = 0;
}

static int irc_connect(Session *s)
{
    IrcImpl *impl = s->impl;
    char port[16];
    snprintf(port, sizeof(port), "%d", impl->port);
    struct addrinfo hints, *res = NULL;
    memset(&hints, 0, sizeof(hints));
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_family = AF_UNSPEC;
    int rc = getaddrinfo(impl->server, port, &hints, &res);
    if (rc != 0) {
        log_error("getaddrinfo(%s): %s", impl->server, gai_strerror(rc));
        return -1;
    }
    int fd = -1;
    for (struct addrinfo *ai = res; ai; ai = ai->ai_next) {
        fd = socket(ai->ai_family, ai->ai_socktype, ai->ai_protocol);
        if (fd < 0) {
            continue;
        }
        if (connect(fd, ai->ai_addr, ai->ai_addrlen) == 0) {
            break;
        }
        close(fd);
        fd = -1;
    }
    freeaddrinfo(res);
    if (fd < 0) {
        log_error("connect to %s:%d failed", impl->server, impl->port);
        return -1;
    }
    impl->fd = fd;
    if (impl->use_ssl) {
        impl->ctx = SSL_CTX_new(TLS_client_method());
        if (impl->ctx == NULL) {
            log_error("SSL_CTX_new failed");
            irc_close(impl);
            return -1;
        }
        if (impl->ssl_verify) {
            SSL_CTX_set_default_verify_paths(impl->ctx);
            SSL_CTX_set_verify(impl->ctx, SSL_VERIFY_PEER, NULL);
        } else {
            SSL_CTX_set_verify(impl->ctx, SSL_VERIFY_NONE, NULL);
        }
        impl->ssl = SSL_new(impl->ctx);
        SSL_set_fd(impl->ssl, impl->fd);
        SSL_set1_host(impl->ssl, impl->server);
        SSL_set_tlsext_host_name(impl->ssl, impl->server);
        if (SSL_connect(impl->ssl) != 1) {
            log_error("TLS handshake with %s failed", impl->server);
            irc_close(impl);
            return -1;
        }
    }
    if (impl->password && impl->password[0]) {
        irc_printf(s, "PASS %s", impl->password);
    }
    irc_printf(s, "NICK %s", s->nick);
    irc_printf(s, "USER %s 0 * :%s", impl->username && impl->username[0] ? impl->username : s->nick,
               pyhole_version_string());
    return 0;
}

static char *nick_from_prefix(const char *prefix)
{
    if (prefix == NULL) {
        return xstrdup("");
    }
    const char *bang = strchr(prefix, '!');
    size_t n = bang ? (size_t)(bang - prefix) : strlen(prefix);
    return xstrndup(prefix, n);
}

static void on_welcome(Session *s)
{
    IrcImpl *impl = s->impl;
    if (impl->identify && impl->identify[0]) {
        irc_printf(s, "PRIVMSG NickServ :IDENTIFY %s", impl->identify);
    }
    for (size_t i = 0; impl->channels && impl->channels[i]; i++) {
        irc_printf(s, "JOIN %s", impl->channels[i]);
    }
}

static void on_privmsg(Session *s, const char *prefix, const char *target, const char *text)
{
    if (text == NULL) {
        return;
    }
    if (text[0] == '\001') {
        if (str_starts_ci(text + 1, "VERSION")) {
            char *nick = nick_from_prefix(prefix);
            irc_printf(s, "NOTICE %s :\001VERSION %s\001", nick, s->version);
            free(nick);
        }
        return;
    }
    bool priv = !str_is_channel(target);
    char *src_nick = nick_from_prefix(prefix);
    Message m = {
        .session = s,
        .text = (char *)text,
        .source = (char *)prefix,
        .target = priv ? src_nick : (char *)target,
    };
    if (priv) {
        log_info("<%s> %s", src_nick, text);
    } else {
        log_info("-%s- <%s> %s", target, src_nick, text);
    }
    hooks_dispatch(s, &m, priv);
    free(src_nick);
}

static void handle_line(Session *s, char *line)
{
    IrcImpl *impl = s->impl;
    log_debug("<< %s", line);
    char *prefix = NULL;
    if (line[0] == ':') {
        prefix = line + 1;
        char *sp = strchr(prefix, ' ');
        if (sp == NULL) {
            return;
        }
        *sp = '\0';
        line = sp + 1;
    }
    while (*line == ' ') {
        line++;
    }
    char *cmd = line;
    char *sp = strchr(cmd, ' ');
    char *rest = NULL;
    if (sp) {
        *sp = '\0';
        rest = sp + 1;
    }
    char *args[8];
    int nargs = 0;
    char *trailing = NULL;
    while (rest && *rest && nargs < 8) {
        while (*rest == ' ') {
            rest++;
        }
        if (*rest == '\0') {
            break;
        }
        if (*rest == ':') {
            trailing = rest + 1;
            break;
        }
        args[nargs++] = rest;
        char *next = strchr(rest, ' ');
        if (next == NULL) {
            rest = NULL;
            break;
        }
        *next = '\0';
        rest = next + 1;
    }

    if (str_eq_ci(cmd, "PING")) {
        irc_printf(s, "PONG :%s", trailing ? trailing : (nargs ? args[0] : ""));
        return;
    }
    if (strcmp(cmd, "001") == 0) {
        if (trailing && strchr(trailing, ' ')) {
            /* keep configured nick */
        }
        log_info("connected to %s as %s", impl->server, s->nick);
        on_welcome(s);
        return;
    }
    if (strcmp(cmd, "433") == 0) {
        char next[80];
        snprintf(next, sizeof(next), "%s%d", s->nick, (int)(time(NULL) % 100));
        log_info("nick in use; trying %s", next);
        set_nick(s, next);
        return;
    }
    if (str_eq_ci(cmd, "PRIVMSG") && nargs >= 1) {
        on_privmsg(s, prefix, args[0], trailing);
        return;
    }
    if (str_eq_ci(cmd, "KICK") && nargs >= 2) {
        if (str_eq_ci(args[1], s->nick)) {
            log_info("kicked from %s; rejoining in %d s", args[0], impl->rejoin_delay);
            sleep((unsigned)impl->rejoin_delay);
            irc_printf(s, "JOIN %s", args[0]);
        }
        return;
    }
    if (str_eq_ci(cmd, "INVITE") && trailing && hooks_is_admin(s, prefix)) {
        join_channel(s, trailing);
    }
}

static int irc_loop(Session *s)
{
    IrcImpl *impl = s->impl;
    for (;;) {
        fd_set rfds;
        FD_ZERO(&rfds);
        FD_SET(impl->fd, &rfds);
        struct timeval tv = {.tv_sec = 60, .tv_usec = 0};
        int rc = select(impl->fd + 1, &rfds, NULL, NULL, &tv);
        if (rc < 0) {
            if (errno == EINTR) {
                continue;
            }
            return -1;
        }
        if (rc == 0) {
            continue;
        }
        char tmp[2048];
        ssize_t n;
        if (impl->ssl) {
            n = SSL_read(impl->ssl, tmp, sizeof(tmp));
        } else {
            n = recv(impl->fd, tmp, sizeof(tmp), 0);
        }
        if (n <= 0) {
            return -1;
        }
        if (impl->readlen + (size_t)n >= sizeof(impl->readbuf)) {
            impl->readlen = 0;
        }
        memcpy(impl->readbuf + impl->readlen, tmp, (size_t)n);
        impl->readlen += (size_t)n;
        impl->readbuf[impl->readlen] = '\0';
        char *start = impl->readbuf;
        char *nl;
        while ((nl = strstr(start, "\n")) != NULL) {
            *nl = '\0';
            if (nl > start && *(nl - 1) == '\r') {
                *(nl - 1) = '\0';
            }
            if (*start) {
                handle_line(s, start);
            }
            start = nl + 1;
        }
        size_t remain = (size_t)(impl->readbuf + impl->readlen - start);
        memmove(impl->readbuf, start, remain);
        impl->readlen = remain;
    }
}

Session *irc_session_new(const Config *cfg, const char *network)
{
    Session *s = xcalloc(1, sizeof(*s));
    IrcImpl *impl = xcalloc(1, sizeof(*impl));
    impl->fd = -1;
    pthread_mutex_init(&impl->wlock, NULL);
    snprintf(s->nick, sizeof(s->nick), "%s", config_get_def(cfg, network, "nick", "pyhole"));
    snprintf(s->command_prefix, sizeof(s->command_prefix), "%s",
             config_get_def(cfg, "Pyhole", "command_prefix", "."));
    s->admins = config_get_list(cfg, "Pyhole", "admins");
    snprintf(s->version, sizeof(s->version), "%s", pyhole_version_string());
    s->impl = impl;
    s->send_privmsg = send_privmsg;
    s->send_notice = send_notice;
    s->op_user = op_user;
    s->deop_user = deop_user;
    s->set_nick = set_nick;
    s->join_channel = join_channel;
    s->part_channel = part_channel;
    snprintf(impl->server, sizeof(impl->server), "%s", config_get_def(cfg, network, "server", ""));
    impl->port = config_get_int(cfg, network, "port", 6667);
    impl->use_ssl = config_get_bool(cfg, network, "ssl", false);
    impl->ssl_verify = config_get_bool(cfg, network, "ssl_verify", true);
    impl->password = xstrdup(config_get_def(cfg, network, "password", ""));
    impl->username = xstrdup(config_get_def(cfg, network, "username", ""));
    impl->identify = xstrdup(config_get_def(cfg, network, "identify_password", ""));
    impl->channels = config_get_list(cfg, network, "channels");
    impl->reconnect_delay = config_get_int(cfg, "Pyhole", "reconnect_delay", 60);
    impl->rejoin_delay = config_get_int(cfg, "Pyhole", "rejoin_delay", 5);
    return s;
}

void irc_session_free(Session *s)
{
    if (s == NULL) {
        return;
    }
    IrcImpl *impl = s->impl;
    if (impl) {
        irc_close(impl);
        pthread_mutex_destroy(&impl->wlock);
        free(impl->password);
        free(impl->username);
        free(impl->identify);
        str_list_free(impl->channels);
        free(impl);
    }
    str_list_free(s->admins);
    free(s);
}

void *irc_run(void *arg)
{
    Session *s = arg;
    IrcImpl *impl = s->impl;
    log_info("Connecting to %s:%d as %s", impl->server, impl->port, s->nick);
    for (;;) {
        if (irc_connect(s) != 0) {
            log_info("retrying in %d seconds", impl->reconnect_delay);
            sleep((unsigned)impl->reconnect_delay);
            continue;
        }
        irc_loop(s);
        log_info("disconnected from %s; reconnecting in %d seconds", impl->server,
                 impl->reconnect_delay);
        irc_close(impl);
        sleep((unsigned)impl->reconnect_delay);
    }
    return NULL;
}
