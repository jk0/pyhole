/* Copyright 2010-2026 Josh Kearney and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
#ifndef PYHOLE_LOG_H
#define PYHOLE_LOG_H

#include <stdbool.h>

void log_init(const char *name, bool debug);
void log_close(void);
void log_info(const char *fmt, ...);
void log_error(const char *fmt, ...);
void log_debug(const char *fmt, ...);

#endif
