/* Copyright 2010-2026 Josh Kearney and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

#include "pyhole/hooks.h"
#include "pyhole/log.h"
#include "pyhole/util.h"

void plugin_admin_register(void);
void plugin_weather_register(void);
void plugin_stocks_register(void);
void plugin_search_register(void);
void plugin_urls_register(void);
void plugin_kernel_register(void);

void plugins_register(char **names)
{
    if (names == NULL) {
        return;
    }
    for (size_t i = 0; names[i]; i++) {
        const char *n = names[i];
        if (str_eq_ci(n, "admin")) {
            plugin_admin_register();
        } else if (str_eq_ci(n, "weather") || str_eq_ci(n, "wunderground")) {
            plugin_weather_register();
        } else if (str_eq_ci(n, "stocks")) {
            plugin_stocks_register();
        } else if (str_eq_ci(n, "search")) {
            plugin_search_register();
        } else if (str_eq_ci(n, "urls")) {
            plugin_urls_register();
        } else if (str_eq_ci(n, "kernel")) {
            plugin_kernel_register();
        } else {
            log_error("unknown plugin '%s' (ignored)", n);
        }
    }
}
