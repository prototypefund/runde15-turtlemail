#!/bin/sh

set -eu

# load environment variables and export them (set -a)
if [ -f /etc/default/turtlemail ]; then
  set -a; . /etc/default/turtlemail; set +a
fi

# run migrations and collect static assets if it looks like we’re starting a web server
if [ "${1:-}" = "runserver" ] || [ "${1:-}" = "uvicorn" ]; then
  poetry --directory /usr/share/turtlemail/ run python3 -m django migrate --no-input
  poetry --directory /usr/share/turtlemail/ run python3 -m django collectstatic --no-input --clear
fi

_is_true() {
  echo "$1" | awk '{print tolower($0)}' | grep -qE "^(1|yes|on|true)$"
}

_status() {
  echo "$1" >&2
}

if [ "${1:-}" = "uvicorn" ]; then
  listen=${2:-0.0.0.0:8000}
  host=$(echo "$listen" | cut -d: -f1)
  port=$(echo "$listen" | cut -d: -f2)
  args=
  if _is_true "${DEBUG:-0}"; then
    _status "debug mode enabled: activating uvicorn reloader"
    args="--reload --reload-dir /usr/share/turtlemail/"
  fi
  # shellcheck disable=SC2086
  exec poetry --directory /usr/share/turtlemail/ run python3 -m uvicorn turtlemail.asgi:application $args \
    --lifespan off \
    --host "$host" \
    --port "$port"
else
  exec poetry --directory /usr/share/turtlemail/ run python3 -m django "$@"
fi
