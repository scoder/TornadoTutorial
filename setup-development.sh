#!/bin/bash

PYTHON=python3.6
VENVDIR=venv

virtualenv -p $PYTHON $VENVDIR  || exit 1
. $VENVDIR/bin/activate

pip install -U pip  || exit 2
pip install -r requirements.txt  || exit 3

echo
echo "virtualenv created in '$VENVDIR'"
