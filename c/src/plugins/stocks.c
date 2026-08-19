/* Copyright 2015-2026 Jason Meridth, Josh Kearney and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

#include "pyhole/hooks.h"
#include "pyhole/http.h"
#include "pyhole/util.h"

#include "../vendor/cJSON.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void quote_symbol(const char *symbol, char *out, size_t outsz)
{
    char url[256];
    snprintf(url, sizeof(url),
             "https://query1.finance.yahoo.com/v8/finance/chart/%s?range=1d&interval=1d", symbol);
    HttpResponse *r = http_get(url);
    if (r == NULL || r->body == NULL) {
        snprintf(out, outsz, "%s: error", symbol);
        http_response_free(r);
        return;
    }
    cJSON *root = cJSON_Parse(r->body);
    http_response_free(r);
    cJSON *chart = root ? cJSON_GetObjectItemCaseSensitive(root, "chart") : NULL;
    cJSON *result = chart ? cJSON_GetObjectItemCaseSensitive(chart, "result") : NULL;
    cJSON *first = result ? cJSON_GetArrayItem(result, 0) : NULL;
    cJSON *meta = first ? cJSON_GetObjectItemCaseSensitive(first, "meta") : NULL;
    cJSON *price = meta ? cJSON_GetObjectItemCaseSensitive(meta, "regularMarketPrice") : NULL;
    cJSON *prev = meta ? cJSON_GetObjectItemCaseSensitive(meta, "chartPreviousClose") : NULL;
    if (!cJSON_IsNumber(price)) {
        snprintf(out, outsz, "%s: n/a", symbol);
        cJSON_Delete(root);
        return;
    }
    if (cJSON_IsNumber(prev)) {
        snprintf(out, outsz, "%s: %.2f (%+.2f)", symbol, price->valuedouble,
                 price->valuedouble - prev->valuedouble);
    } else {
        snprintf(out, outsz, "%s: %.2f", symbol, price->valuedouble);
    }
    cJSON_Delete(root);
}

static void stocks_work(Message *m, const char *params)
{
    char **syms = str_split_list(params);
    char **parts = xcalloc(str_list_len(syms) + 1, sizeof(*parts));
    size_t n = 0;
    for (size_t i = 0; syms[i]; i++) {
        char symbol[16];
        size_t k = 0;
        for (const char *p = syms[i]; *p && k + 1 < sizeof(symbol); p++) {
            if (!isspace((unsigned char)*p)) {
                symbol[k++] = (char)toupper((unsigned char)*p);
            }
        }
        symbol[k] = '\0';
        if (symbol[0] == '\0') {
            continue;
        }
        char buf[64];
        quote_symbol(symbol, buf, sizeof(buf));
        parts[n++] = xstrdup(buf);
    }
    str_list_free(syms);
    if (n == 0) {
        message_dispatch(m, "Unable to fetch stock data.");
        free(parts);
        return;
    }
    char *joined = str_join(parts, ", ");
    message_dispatch(m, joined);
    free(joined);
    str_list_free(parts);
}

static void cmd_stock(Message *m, const char *params)
{
    if (params == NULL || *params == '\0') {
        message_dispatch(m, "Display current stock values (ex: .stock aapl,msft).");
        return;
    }
    hook_spawn(stocks_work, m, params);
}

void plugin_stocks_register(void)
{
    hook_add_command("stock", cmd_stock, "Display current stock values (ex: .stock aapl,msft).");
}
