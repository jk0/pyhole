# pyhole

A small IRC bot. Commands, keywords, and regex watchers are compiled-in plugins.

This branch is the **C11 port**. Slack, Flask, PagerDuty, and the other optional Python plugins are not here.

## Build

Needs a C11 compiler, libcurl, and OpenSSL.

```bash
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

See [`pyhole.conf.sample`](pyhole.conf.sample). IRC only: `server`, `nick`, `channels`, optional `ssl` / `ssl_verify` / `identify_password`. `plugins` is a comma-separated list of built-in modules.

## Plugins

| Name | Commands |
|---|---|
| `admin` | `.help` `.version` `.op` `.deop` `.nick` `.join` `.part` `.say` |
| `weather` | `.weather` / `.w <location>` (Open-Meteo) |
| `stocks` | `.stock aapl,msft` |
| `search` | `.urban` `.wikipedia` |
| `urls` | `.title <url>`; auto-title YouTube/Spotify |
| `kernel` | `.kernel` |

Admin commands require `nick!ident` in `admins`.

## Layout

```
include/pyhole/   public headers
src/              core (config, IRC, HTTP, hooks)
src/plugins/      compiled-in plugins
src/vendor/       cJSON
tests/            no-network unit tests
```

## License

Apache License 2.0. See `LICENSE`.
