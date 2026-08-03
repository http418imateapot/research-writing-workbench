#!/usr/bin/env sh
set -eu
exec ./.venv/bin/python build.py "$@"
