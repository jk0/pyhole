#!/bin/bash
# Copyright 2016-2026 Josh Kearney and contributors
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

docker build -t pyhole .
docker stop pyhole 2>/dev/null || true
docker rm pyhole 2>/dev/null || true
docker run -d \
  --name pyhole \
  -e PYHOLE_HOME=/data \
  -v "${PYHOLE_DATA:-$HOME/.pyhole}:/data" \
  pyhole
docker ps --filter name=pyhole
docker logs -f pyhole
