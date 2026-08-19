/* Copyright 2010-2026 Josh Kearney and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
#ifndef PYHOLE_HTTP_H
#define PYHOLE_HTTP_H

#include <stddef.h>

typedef struct {
    long status;
    char *body;
    size_t body_len;
    char *content_type;
} HttpResponse;

void http_global_init(void);
void http_global_cleanup(void);

HttpResponse *http_get(const char *url);
void http_response_free(HttpResponse *r);

#endif
