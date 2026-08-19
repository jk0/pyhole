/* Copyright 2011-2026 Josh Kearney and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

#include "pyhole/hooks.h"
#include "pyhole/http.h"
#include "pyhole/util.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void kernel_work(Message *m, const char *params)
{
    (void)params;
    HttpResponse *r = http_get("https://www.kernel.org/kdist/finger_banner");
    if (r == NULL || r->body == NULL) {
        http_response_free(r);
        return;
    }
    const char *line = r->body;
    while (line && *line) {
        const char *nl = strchr(line, '\n');
        size_t n = nl ? (size_t)(nl - line) : strlen(line);
        char buf[256];
        if (n >= sizeof(buf)) {
            n = sizeof(buf) - 1;
        }
        memcpy(buf, line, n);
        buf[n] = '\0';
        if (strstr(buf, "mainline")) {
            char *p = buf;
            char *w = buf;
            int spaces = 0;
            while (*p) {
                if (*p == ' ') {
                    spaces++;
                    if (spaces > 1) {
                        p++;
                        continue;
                    }
                } else {
                    spaces = 0;
                }
                *w++ = *p++;
            }
            *w = '\0';
            message_dispatch(m, str_trim(buf));
            break;
        }
        line = nl ? nl + 1 : NULL;
    }
    http_response_free(r);
}

static void cmd_kernel(Message *m, const char *params)
{
    (void)params;
    hook_spawn(kernel_work, m, NULL);
}

void plugin_kernel_register(void)
{
    hook_add_command("kernel", cmd_kernel, "Retrieve the current kernel version (ex: .kernel).");
}
