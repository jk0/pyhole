/* Copyright 2011-2026 Josh Kearney and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

#include "pyhole/hooks.h"
#include "pyhole/http.h"
#include "pyhole/util.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static char *extract_title(const char *html)
{
    if (html == NULL) {
        return NULL;
    }
    const char *start = NULL;
    for (const char *p = html; *p; p++) {
        if (str_starts_ci(p, "<title")) {
            const char *gt = strchr(p, '>');
            if (gt) {
                start = gt + 1;
                break;
            }
        }
    }
    if (start == NULL) {
        return NULL;
    }
    const char *end = NULL;
    for (const char *p = start; *p; p++) {
        if (str_starts_ci(p, "</title>")) {
            end = p;
            break;
        }
    }
    if (end == NULL) {
        return NULL;
    }
    char *raw = xstrndup(start, (size_t)(end - start));
    char *decoded = decode_entities(raw);
    free(raw);
    return decoded;
}

static void title_work(Message *m, const char *url)
{
    char cleaned[1024];
    snprintf(cleaned, sizeof(cleaned), "%s", url);
    char *lt = strchr(cleaned, '<');
    if (lt) {
        *lt = '\0';
    }
    char *pipe = strchr(cleaned, '|');
    if (pipe) {
        *pipe = '\0';
    }
    char *gt = strchr(cleaned, '>');
    if (gt) {
        *gt = '\0';
    }
    char full[1088];
    if (!str_starts(cleaned, "http://") && !str_starts(cleaned, "https://")) {
        snprintf(full, sizeof(full), "http://%s", cleaned);
    } else {
        snprintf(full, sizeof(full), "%s", cleaned);
    }
    HttpResponse *r = http_get(full);
    if (r == NULL || r->body == NULL) {
        http_response_free(r);
        return;
    }
    char *title = extract_title(r->body);
    if (title && title[0]) {
        char buf[512];
        snprintf(buf, sizeof(buf), "%s (%s)", title, r->content_type ? r->content_type : "");
        message_dispatch(m, buf);
    } else {
        char buf[320];
        snprintf(buf, sizeof(buf), "No title found: %s", full);
        message_dispatch(m, buf);
    }
    free(title);
    http_response_free(r);
}

static bool interesting_host(const char *url)
{
    const char *host = strstr(url, "://");
    host = host ? host + 3 : url;
    return str_starts(host, "www.youtube.com") || str_starts(host, "youtu.be") ||
           str_starts(host, "open.spotify.com");
}

static void cmd_title(Message *m, const char *params)
{
    if (params == NULL || *params == '\0') {
        message_dispatch(m, "Display the title of a URL (ex: .title <url>).");
        return;
    }
    hook_spawn(title_work, m, params);
}

static void on_url(Message *m, const char *match)
{
    if (interesting_host(match)) {
        hook_spawn(title_work, m, match);
    }
}

void plugin_urls_register(void)
{
    hook_add_command("title", cmd_title, "Display the title of a URL (ex: .title <url>).");
    hook_add_regex("https?://[^> ]+", on_url, "Watch for URLs.");
}
