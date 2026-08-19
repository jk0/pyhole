/* Copyright 2010-2026 Josh Kearney and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

#include "pyhole/http.h"

#include "pyhole/util.h"
#include "pyhole/version.h"

#include <curl/curl.h>
#include <stdlib.h>
#include <string.h>

struct Buf {
    char *data;
    size_t len;
};

static size_t write_cb(char *ptr, size_t size, size_t nmemb, void *userdata)
{
    struct Buf *b = userdata;
    size_t n = size * nmemb;
    char *grown = realloc(b->data, b->len + n + 1);
    if (grown == NULL) {
        return 0;
    }
    b->data = grown;
    memcpy(b->data + b->len, ptr, n);
    b->len += n;
    b->data[b->len] = '\0';
    return n;
}

void http_global_init(void)
{
    curl_global_init(CURL_GLOBAL_DEFAULT);
}

void http_global_cleanup(void)
{
    curl_global_cleanup();
}

HttpResponse *http_get(const char *url)
{
    HttpResponse *r = xcalloc(1, sizeof(*r));
    struct Buf buf = {0};
    buf.data = xstrdup("");
    CURL *curl = curl_easy_init();
    if (curl == NULL) {
        http_response_free(r);
        free(buf.data);
        return NULL;
    }
    curl_easy_setopt(curl, CURLOPT_URL, url);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_cb);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &buf);
    curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, 15L);
    curl_easy_setopt(curl, CURLOPT_CONNECTTIMEOUT, 10L);
    curl_easy_setopt(curl, CURLOPT_USERAGENT, "pyhole/" PYHOLE_VERSION);
    CURLcode rc = curl_easy_perform(curl);
    if (rc != CURLE_OK) {
        curl_easy_cleanup(curl);
        free(buf.data);
        http_response_free(r);
        return NULL;
    }
    curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &r->status);
    char *ct = NULL;
    curl_easy_getinfo(curl, CURLINFO_CONTENT_TYPE, &ct);
    if (ct) {
        r->content_type = xstrdup(ct);
    }
    curl_easy_cleanup(curl);
    r->body = buf.data;
    r->body_len = buf.len;
    return r;
}

void http_response_free(HttpResponse *r)
{
    if (r == NULL) {
        return;
    }
    free(r->body);
    free(r->content_type);
    free(r);
}
