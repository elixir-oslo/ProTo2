#!/bin/sh

HERE=$(dirname "$0")

cd "$HERE"

export PYTHONPATH=$PYTHONPATH:$HERE/lib

python lib/proto/protoToolExecute.py $GALAXY_OUTPUT
