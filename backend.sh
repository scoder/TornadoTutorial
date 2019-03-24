#!/usr/bin/env bash

VENVDIR=venv

[ -f $VENVDIR/bin/activate ] || {
    echo "please create virtualenv first by running setup-development.sh"
    exit 1
}

. $VENVDIR/bin/activate

python -m fortunes.serve
