#!/usr/bin/env bash

set -e
set -x

export $(grep -v '^#' .env.test | xargs)

if [ "$SQL_DB__HOST" != "localhost" ] && [ "$SQL_DB__HOST" != "127.0.0.1" ]; then
    echo "SQL_DB__HOST is not set to localhost or 127.0.0.1. Exiting."
    exit 1
fi

poetry run python -m coverage run -m pytest -lv ${ARGS}
poetry run python -m coverage report -m
