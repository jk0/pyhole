/* Copyright 2010-2026 Josh Kearney and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

#include "pyhole/log.h"

#include <pthread.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

static FILE *g_fp;
static bool g_debug;
static pthread_mutex_t g_lock = PTHREAD_MUTEX_INITIALIZER;

void log_init(const char *name, bool debug)
{
    g_debug = debug;
    if (name == NULL) {
        return;
    }
    g_fp = fopen(name, "a");
}

void log_close(void)
{
    pthread_mutex_lock(&g_lock);
    if (g_fp) {
        fclose(g_fp);
        g_fp = NULL;
    }
    pthread_mutex_unlock(&g_lock);
}

static void emit(const char *level, const char *fmt, va_list ap)
{
    char timebuf[16];
    time_t now = time(NULL);
    struct tm tm_now;
    localtime_r(&now, &tm_now);
    strftime(timebuf, sizeof(timebuf), "%H:%M:%S", &tm_now);

    pthread_mutex_lock(&g_lock);
    fprintf(stderr, "%s [%s] ", timebuf, level);
    va_list ap2;
    va_copy(ap2, ap);
    vfprintf(stderr, fmt, ap);
    fputc('\n', stderr);
    if (g_fp) {
        fprintf(g_fp, "%s [%s] ", timebuf, level);
        vfprintf(g_fp, fmt, ap2);
        fputc('\n', g_fp);
        fflush(g_fp);
    }
    va_end(ap2);
    pthread_mutex_unlock(&g_lock);
}

void log_info(const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    emit("info", fmt, ap);
    va_end(ap);
}

void log_error(const char *fmt, ...)
{
    va_list ap;
    va_start(ap, fmt);
    emit("error", fmt, ap);
    va_end(ap);
}

void log_debug(const char *fmt, ...)
{
    if (!g_debug) {
        return;
    }
    va_list ap;
    va_start(ap, fmt);
    emit("debug", fmt, ap);
    va_end(ap);
}
