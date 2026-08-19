/* Copyright 2010-2026 Josh Kearney and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

#include "pyhole/config.h"
#include "pyhole/hooks.h"
#include "pyhole/http.h"
#include "pyhole/irc.h"
#include "pyhole/log.h"
#include "pyhole/util.h"
#include "pyhole/version.h"

#include <errno.h>
#include <getopt.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

static char *home_dir(void)
{
    const char *env = getenv("PYHOLE_HOME");
    if (env && *env) {
        return xstrdup(env);
    }
    const char *home = getenv("HOME");
    if (home == NULL) {
        return xstrdup(".");
    }
    size_t n = strlen(home) + 16;
    char *p = xmalloc(n);
    snprintf(p, n, "%s/.pyhole", home);
    return p;
}

static int ensure_dir(const char *path)
{
    if (mkdir(path, 0700) == 0 || errno == EEXIST) {
        return 0;
    }
    perror(path);
    return -1;
}

static char *default_conf(void)
{
    char *home = home_dir();
    size_t n = strlen(home) + 16;
    char *p = xmalloc(n);
    snprintf(p, n, "%s/pyhole.conf", home);
    free(home);
    return p;
}

static int copy_sample(const char *dest)
{
    const char *candidates[] = {
        "c/pyhole.conf.sample",
        "pyhole.conf.sample",
        NULL,
    };
    FILE *in = NULL;
    for (int i = 0; candidates[i]; i++) {
        in = fopen(candidates[i], "r");
        if (in) {
            break;
        }
    }
    if (in == NULL) {
        fprintf(stderr, "could not find pyhole.conf.sample\n");
        return -1;
    }
    FILE *out = fopen(dest, "w");
    if (out == NULL) {
        perror(dest);
        fclose(in);
        return -1;
    }
    char buf[4096];
    size_t n;
    while ((n = fread(buf, 1, sizeof(buf), in)) > 0) {
        fwrite(buf, 1, n, out);
    }
    fclose(in);
    fclose(out);
    printf("Copied sample configuration file to: %s\n", dest);
    printf("Please edit it before running again.\n");
    return 0;
}

int main(int argc, char **argv)
{
    const char *conf_path = NULL;
    bool debug = false;
    int opt;
    while ((opt = getopt(argc, argv, "c:dVh")) != -1) {
        switch (opt) {
        case 'c':
            conf_path = optarg;
            break;
        case 'd':
            debug = true;
            break;
        case 'V':
            puts(pyhole_version_string());
            return 0;
        case 'h':
        default:
            fprintf(stderr, "usage: pyhole [-c config] [-d] [-V]\n");
            return opt == 'h' ? 0 : 2;
        }
    }

    char *home = home_dir();
    ensure_dir(home);
    char *owned_conf = NULL;
    if (conf_path == NULL) {
        owned_conf = default_conf();
        conf_path = owned_conf;
    }
    if (access(conf_path, R_OK) != 0) {
        if (copy_sample(conf_path) != 0) {
            return 1;
        }
        free(owned_conf);
        free(home);
        return 0;
    }

    Config *cfg = config_load(conf_path);
    if (cfg == NULL) {
        fprintf(stderr, "unable to load %s\n", conf_path);
        return 1;
    }
    debug = debug || config_get_bool(cfg, "Pyhole", "debug", false);

    char logfile[512];
    snprintf(logfile, sizeof(logfile), "%s/pyhole.log", home);
    log_init(logfile, debug);
    log_info("Starting %s", pyhole_version_string());

    http_global_init();
    char **plugins = config_get_list(cfg, "Pyhole", "plugins");
    plugins_register(plugins);
    str_list_free(plugins);

    char **networks = config_get_list(cfg, "Pyhole", "networks");
    size_t nnet = str_list_len(networks);
    if (nnet == 0) {
        log_error("no networks configured");
        return 1;
    }

    pthread_t *threads = xcalloc(nnet, sizeof(*threads));
    Session **sessions = xcalloc(nnet, sizeof(*sessions));
    size_t started = 0;
    for (size_t i = 0; i < nnet; i++) {
        if (config_get(cfg, networks[i], "api_token")) {
            log_error("skipping %s: Slack networks are not supported in the C port", networks[i]);
            continue;
        }
        if (config_get(cfg, networks[i], "server") == NULL) {
            log_error("skipping %s: no server", networks[i]);
            continue;
        }
        sessions[started] = irc_session_new(cfg, networks[i]);
        if (pthread_create(&threads[started], NULL, irc_run, sessions[started]) != 0) {
            log_error("pthread_create failed for %s", networks[i]);
            irc_session_free(sessions[started]);
            sessions[started] = NULL;
            continue;
        }
        started++;
    }

    if (started == 0) {
        log_error("no IRC networks started");
        return 1;
    }

    for (size_t i = 0; i < started; i++) {
        pthread_join(threads[i], NULL);
    }

    http_global_cleanup();
    hooks_reset();
    config_free(cfg);
    str_list_free(networks);
    free(threads);
    free(sessions);
    free(owned_conf);
    free(home);
    log_close();
    return 0;
}
