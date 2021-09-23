#!/bin/sh

HERE=$(dirname "$0")
INPUTS=$1

#cd "$HERE"

export PYTHONPATH=$PYTHONPATH:$HERE/lib

cat "$INPUTS" > "$GALAXY_OUTPUT"
cat "$INPUTS"

python -V

python $HERE/lib/proto/protoToolExecute.py "$GALAXY_OUTPUT"
