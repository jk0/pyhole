# pyhole

A C port of the IRC core lives in [`c/`](c/README.md) (branch `c-port`): no Slack, no HTTP API.

A modular IRC and Slack bot. Commands, keywords, regex watchers, and background polls are plugins; each network runs in its own process.

This tree is a Python 3.12+ rewrite of the original 2010–2016 pyhole. Plugin hook names (`hook_add_command`, `hook_add_keyword`, `hook_add_msg_regex`, `hook_add_poll`) are unchanged.

## Requirements

- Python 3.12 or newer
- An IRC network and/or a Slack app with Socket Mode enabled

## Install

```bash
git clone https://github.com/jk0/pyhole.git
cd pyhole
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Optional Launchpad plugin:

```bash
pip install -e ".[launchpad]"
```

## Configure

On first run, pyhole copies a sample config into `~/.pyhole/pyhole.conf` (or `$PYHOLE_HOME/pyhole.conf`) and exits:

```bash
pyhole
```

Edit that file:

- `networks` — INI section names, one per IRC or Slack connection
- `plugins` — module names from `pyhole/plugins/` (and `~/.pyhole/plugins/`)
- `admins` — `nick!ident` for IRC, Slack usernames for Slack
- IRC sections need `server`, `nick`, `channels`; Slack sections need `api_token` (`xoxb-...`) and `app_token` (`xapp-...`)

Override the config path with `-c /path/to/pyhole.conf`. Debug logging: `-d` or `debug = True`.

Libera Chat (formerly Freenode) is the sample IRC network. Slack uses [Socket Mode](https://api.slack.com/apis/connections/socket); the old RTM client is gone.

## Run

```bash
pyhole
python -m pyhole
pyhole -c ./pyhole.conf -d
```

## Tests and lint

```bash
pytest
ruff check .
ruff format .
```

## Docker

```bash
docker build -t pyhole .
docker run --rm -e PYHOLE_HOME=/data -v pyhole-data:/data pyhole
```

Or `bash tools/docker_deploy.sh` after editing it for your host paths.

## Plugins

Built-in modules (enable them in `plugins = ...`):

| Module | Commands / hooks | Notes |
|---|---|---|
| `admin` | `.help` `.version` `.reload` `.op` `.deop` `.nick` `.join` `.part` `.say` | `.reload` and channel ops are admin-only |
| `weather` | `.weather` / `.w` | Open-Meteo, no API key. `.w set Austin` remembers a location |
| `wunderground` | alias of `weather` | Old name still imports |
| `stocks` | `.stock aapl,msft` | Yahoo Finance chart API |
| `search` | `.urban` `.wikipedia` | Urban Dictionary JSON + Wikipedia OpenSearch |
| `urls` | `.title`, auto-title YouTube/Spotify URLs | |
| `kernel` | `.kernel` | kernel.org finger banner |
| `allergies` | `.allergies` `.pollen` | San Antonio, TX |
| `distance` | `.distance` | Google Maps; needs `[GoogleMaps] key=` |
| `boxoffice` | `.boxoffice` | TMDB now-playing; needs `[TMDB] key=` |
| `jira` | `AB-1234` | Needs `[Jira]`; TLS verified by default |
| `redmine` | `.rbugs` `RM12345` | API key sent as `X-Redmine-API-Key`, not in the URL |
| `ops` | `.query` `.ack` `.resolve` `.note` `.oncall` `.alert` … | PagerDuty |
| `launchpad` | `.lbugs` `LP12345` | Optional extra |
| `xsa` | `xsa123`, poll | Xen Security Advisories |

A plugin is a `Plugin` subclass. User plugins go in `~/.pyhole/plugins/*.py` and are listed in `plugins` the same way.

```python
from pyhole.core import plugin, utils


class Example(plugin.Plugin):
    """An example plugin."""

    @plugin.hook_add_command("test")
    @utils.require_params
    def test(self, message, params=None, **kwargs):
        """An example command (ex: .test foo)."""
        message.dispatch(params)
```

## HTTP API

Disabled by default (`api_enabled = False`). When enabled it binds `api_host` (default `127.0.0.1`) and `api_port` (default `5000`):

- `GET /` — version string
- `POST /pastes` — JSON `{"paste": "..."}`; optional `network` + `target` to announce the URL
- `GET /pastes/<id>` and `GET /pastes/<id>/raw`
- `POST /messages/send` — JSON `{"network", "target", "message"}`
- PagerDuty HTML views under `/pagerduty...` if `[PagerDuty]` is configured

Set `api_auth_token` and send `Authorization: Bearer ...` on the POST routes and PagerDuty pages.

## What changed in 1.0

- Python 3.12+, `pyproject.toml`, pytest, ruff, GitHub Actions
- Slack Socket Mode (`slack-sdk`) instead of the dead RTM client
- IRC TLS via `ssl.SSLContext` (`ssl.wrap_socket` was removed in 3.12)
- HTTP timeouts on every request
- Weather via Open-Meteo (Weather Underground is gone)
- Stocks via Yahoo's public chart API (`yahoo-finance` is gone)
- Urban Dictionary and Wikipedia talk to real JSON APIs instead of scraping
- Box office uses TMDB instead of scraping Rotten Tomatoes
- Redmine no longer puts the API key in the URL
- Jira verifies TLS unless you set `verify_ssl = False`
- Plugin poll loops can be stopped on `.reload`
- Config errors raise instead of `sys.exit` from library code
- API defaults to localhost; optional bearer auth

## License

Apache License 2.0. See `LICENSE` and `AUTHORS`.
