/* Copyright 2026 Josh Kearney and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

#include "pyhole/config.h"
#include "pyhole/util.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(void)
{
    const char *path = "/tmp/pyhole-test.conf";
    FILE *fp = fopen(path, "w");
    if (fp == NULL) {
        perror(path);
        return 1;
    }
    fputs("[Pyhole]\ncommand_prefix = .\ndebug = False\nreconnect_delay = 60\n"
          "admins = alice!ident, bob!ident\nplugins = admin, weather\n"
          "[Libera]\nserver = irc.libera.chat\nssl = True\n",
          fp);
    fclose(fp);

    Config *c = config_load(path);
    if (c == NULL) {
        fprintf(stderr, "config_load failed\n");
        return 1;
    }
    int rc = 0;
    if (strcmp(config_get(c, "Pyhole", "command_prefix"), ".") != 0) {
        fprintf(stderr, "prefix\n");
        rc = 1;
    }
    if (config_get_int(c, "Pyhole", "reconnect_delay", 0) != 60) {
        fprintf(stderr, "int\n");
        rc = 1;
    }
    if (config_get_bool(c, "Pyhole", "debug", true) != false) {
        fprintf(stderr, "bool\n");
        rc = 1;
    }
    if (config_get_bool(c, "Libera", "ssl", false) != true) {
        fprintf(stderr, "ssl\n");
        rc = 1;
    }
    char **admins = config_get_list(c, "Pyhole", "admins");
    if (str_list_len(admins) != 2 || !str_list_contains(admins, "alice!ident")) {
        fprintf(stderr, "list\n");
        rc = 1;
    }
    str_list_free(admins);
    config_free(c);
    unlink(path);
    if (rc == 0) {
        puts("test_config ok");
    }
    return rc;
}
