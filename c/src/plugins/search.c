/* Copyright 2010-2026 Josh Kearney and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

#include "pyhole/hooks.h"
#include "pyhole/http.h"
#include "pyhole/util.h"

#include "../vendor/cJSON.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static char *url_encode(const char *s)
{
    size_t cap = strlen(s) * 3 + 1;
    char *out = xmalloc(cap);
    size_t n = 0;
    for (; *s; s++) {
        unsigned char c = (unsigned char)*s;
        if ((c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == '-' ||
            c == '_' || c == '.') {
            out[n++] = (char)c;
        } else if (c == ' ') {
            out[n++] = '%';
            out[n++] = '2';
            out[n++] = '0';
        } else {
            n += (size_t)snprintf(out + n, cap - n, "%%%02X", c);
        }
    }
    out[n] = '\0';
    return out;
}

static void urban_work(Message *m, const char *params)
{
    char *q = url_encode(params);
    char url[768];
    snprintf(url, sizeof(url), "https://api.urbandictionary.com/v0/define?term=%s", q);
    free(q);
    HttpResponse *r = http_get(url);
    cJSON *root = r && r->body ? cJSON_Parse(r->body) : NULL;
    http_response_free(r);
    cJSON *list = root ? cJSON_GetObjectItemCaseSensitive(root, "list") : NULL;
    cJSON *first = list ? cJSON_GetArrayItem(list, 0) : NULL;
    cJSON *def = first ? cJSON_GetObjectItemCaseSensitive(first, "definition") : NULL;
    cJSON *ex = first ? cJSON_GetObjectItemCaseSensitive(first, "example") : NULL;
    if (!cJSON_IsString(def)) {
        char buf[160];
        snprintf(buf, sizeof(buf), "No results found: '%s'", params);
        message_dispatch(m, buf);
        cJSON_Delete(root);
        return;
    }
    char *meaning = decode_entities(def->valuestring);
    if (cJSON_IsString(ex) && ex->valuestring[0]) {
        char *example = decode_entities(ex->valuestring);
        char buf[1024];
        snprintf(buf, sizeof(buf), "%s (ex: %s)", meaning, example);
        message_dispatch(m, buf);
        free(example);
    } else {
        message_dispatch(m, meaning);
    }
    free(meaning);
    cJSON_Delete(root);
}

static void wiki_work(Message *m, const char *params)
{
    char *q = url_encode(params);
    char url[768];
    snprintf(url, sizeof(url),
             "https://en.wikipedia.org/w/api.php?action=opensearch&search=%s&limit=4"
             "&namespace=0&format=json",
             q);
    free(q);
    HttpResponse *r = http_get(url);
    cJSON *root = r && r->body ? cJSON_Parse(r->body) : NULL;
    http_response_free(r);
    cJSON *urls = root && cJSON_IsArray(root) ? cJSON_GetArrayItem(root, 3) : NULL;
    if (urls == NULL || cJSON_GetArraySize(urls) == 0) {
        char buf[160];
        snprintf(buf, sizeof(buf), "No results found: '%s'", params);
        message_dispatch(m, buf);
        cJSON_Delete(root);
        return;
    }
    cJSON *item;
    cJSON_ArrayForEach(item, urls)
    {
        if (cJSON_IsString(item)) {
            message_dispatch(m, item->valuestring);
        }
    }
    cJSON_Delete(root);
}

static void cmd_urban(Message *m, const char *params)
{
    if (params == NULL || *params == '\0') {
        message_dispatch(m, "Search Urban Dictionary (ex: .urban <query>).");
        return;
    }
    hook_spawn(urban_work, m, params);
}

static void cmd_wikipedia(Message *m, const char *params)
{
    if (params == NULL || *params == '\0') {
        message_dispatch(m, "Search Wikipedia (ex: .wikipedia <query>).");
        return;
    }
    hook_spawn(wiki_work, m, params);
}

void plugin_search_register(void)
{
    hook_add_command("urban", cmd_urban, "Search Urban Dictionary (ex: .urban <query>).");
    hook_add_command("wikipedia", cmd_wikipedia, "Search Wikipedia (ex: .wikipedia <query>).");
}
