/* Copyright 2010-2026 Josh Kearney and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
#ifndef PYHOLE_IRC_H
#define PYHOLE_IRC_H

#include "pyhole/config.h"
#include "pyhole/hooks.h"

Session *irc_session_new(const Config *cfg, const char *network);
void irc_session_free(Session *s);
void *irc_run(void *session);

#endif
