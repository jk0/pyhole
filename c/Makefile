CC ?= cc
CFLAGS ?= -std=c11 -Wall -Wextra -Wpedantic -O2 -g
CPPFLAGS += -Iinclude -Isrc/vendor
LDFLAGS ?=
LIBS = -lcurl -lssl -lcrypto

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
OPENSSL_PREFIX ?= /opt/homebrew/opt/openssl@3
ifneq ($(wildcard $(OPENSSL_PREFIX)/include/openssl/ssl.h),)
CPPFLAGS += -I$(OPENSSL_PREFIX)/include
LDFLAGS += -L$(OPENSSL_PREFIX)/lib
endif
else
LIBS += -lpthread
endif

CORE_SRC = \
	src/config.c \
	src/hooks.c \
	src/http.c \
	src/irc.c \
	src/log.c \
	src/util.c \
	src/version.c \
	src/vendor/cJSON.c

PLUGIN_SRC = \
	src/plugins/admin.c \
	src/plugins/weather.c \
	src/plugins/stocks.c \
	src/plugins/search.c \
	src/plugins/urls.c \
	src/plugins/kernel.c \
	src/plugins/register.c

SRC = $(CORE_SRC) $(PLUGIN_SRC) src/main.c
OBJ = $(SRC:.c=.o)

.PHONY: all clean test

all: pyhole

pyhole: $(OBJ)
	$(CC) $(LDFLAGS) -o $@ $(OBJ) $(LIBS)

src/%.o: src/%.c
	$(CC) $(CPPFLAGS) $(CFLAGS) -c -o $@ $<

TEST_CORE = src/config.c src/hooks.c src/log.c src/util.c src/version.c
TEST_PLUGINS = src/plugins/admin.c

test: tests/test_config tests/test_util tests/test_hooks
	./tests/test_config
	./tests/test_util
	./tests/test_hooks

tests/test_config: tests/test_config.c $(TEST_CORE)
	$(CC) $(CPPFLAGS) $(CFLAGS) $(LDFLAGS) -o $@ tests/test_config.c $(TEST_CORE)

tests/test_util: tests/test_util.c src/util.c src/log.c
	$(CC) $(CPPFLAGS) $(CFLAGS) $(LDFLAGS) -o $@ tests/test_util.c src/util.c src/log.c

tests/test_hooks: tests/test_hooks.c $(TEST_CORE)
	$(CC) $(CPPFLAGS) $(CFLAGS) $(LDFLAGS) -o $@ tests/test_hooks.c $(TEST_CORE)

clean:
	rm -f $(OBJ) pyhole tests/test_config tests/test_util tests/test_hooks
