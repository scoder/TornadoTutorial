#!/bin/bash

PYTHON=python3
VENVDIR=venv

$PYTHON -c "import sys; assert sys.version_info >= (3, 7)"

$PYTHON -m venv $VENVDIR  || exit 1

$VENVDIR/bin/pip install -U pip setuptools || exit 2
$VENVDIR/bin/pip install -r requirements.txt  || exit 3

echo
echo "venv created in '$VENVDIR'"
