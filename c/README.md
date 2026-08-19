# pyhole (C port)

A small IRC bot with the original pyhole plugin idea: commands, keywords, and regex watchers. This is a from-scratch C11 rewrite of the Python 1.0 core.

**Intentionally not ported:** Slack, the Flask HTTP API, PagerDuty, Jira, Redmine, Launchpad, box office, distance, allergies, and XSA polling. Those were either dead APIs, optional SaaS clients, or not worth the C surface area.

## Build

Needs a C11 compiler, libcurl, and OpenSSL.

```bash
cd c
make
make test
```

On macOS with Homebrew OpenSSL:

```bash
make OPENSSL_PREFIX=/opt/homebrew/opt/openssl@3
```

## Run

```bash
./pyhole -c pyhole.conf.sample   # edit a real copy first
./pyhole                         # copies ~/.pyhole/pyhole.conf on first run
./pyhole -d                      # debug logging
```

`PYHOLE_HOME` overrides `~/.pyhole`.

## Config

See `pyhole.conf.sample`. IRC only: `server`, `nick`, `channels`, optional `ssl` / `ssl_verify` / `identify_password`. `plugins` is a comma-separated list of built-in modules.

## Plugins

| Name | Commands |
|---|---|
| `admin` | `.help` `.version` `.op` `.deop` `.nick` `.join` `.part` `.say` |
| `weather` | `.weather` / `.w <location>` (Open-Meteo) |
| `stocks` | `.stock aapl,msft` |
| `search` | `.urban` `.wikipedia` |
| `urls` | `.title <url>`; auto-title YouTube/Spotify |
| `kernel` | `.kernel` |

Admin commands still require `nick!ident` in `admins`.

## Layout

```
include/pyhole/   public headers
src/              core (config, IRC, HTTP, hooks)
src/plugins/      compiled-in plugins
src/vendor/       cJSON
tests/            no-network unit tests
```
