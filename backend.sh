#!/usr/bin/env bash

[ -f venv/bin/activate ] || {
    echo "please create virtualenv first by running setup-development.sh"
    exit 1
}

. venv/bin/activate

python -m fortunes.serve
