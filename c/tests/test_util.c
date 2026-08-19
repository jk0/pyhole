/* Copyright 2026 Josh Kearney and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

#include "pyhole/util.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int fails;

static void expect_true(const char *name, bool v)
{
    if (!v) {
        fprintf(stderr, "FAIL %s\n", name);
        fails++;
    }
}

int main(void)
{
    char *d = decode_entities("<foo>&#64;&amp;bar&amp;&#64;</foo>");
    expect_true("decode_entities", strcmp(d, "@&bar&@") == 0);
    free(d);

    int n = 0;
    expect_true("ensure_int 3", ensure_int("3", &n) && n == 3);
    expect_true("ensure_int a", !ensure_int("a", &n));
    expect_true("ensure_int -123", ensure_int("-123", &n) && n == 123);

    char **list = str_split_list("a, b, c");
    expect_true("list len", str_list_len(list) == 3);
    expect_true("list contains", str_list_contains(list, "b"));
    str_list_free(list);

    expect_true("channel", str_is_channel("#chan"));
    expect_true("not channel", !str_is_channel("nick"));
    expect_true("starts ci", str_starts_ci("HELP me", "help"));

    if (fails) {
        fprintf(stderr, "%d failures\n", fails);
        return 1;
    }
    puts("test_util ok");
    return 0;
}
