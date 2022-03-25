#!/bin/bash --login

conda activate proto2

HERE=$(dirname "$0")
INPUTS=$1

#cd "$HERE"

export PYTHONPATH=$PYTHONPATH:$HERE/lib

cat "$INPUTS" > "$GALAXY_OUTPUT"
cat "$INPUTS"

python -V

#echo {"type": "dataset", "dataset_id": ${GALAXY_OUTPUT_ID}, "name": "my dynamic name", "ext": "txt", "info": "my dynamic info", "dbkey": "cust1"} > galaxy.json

python $HERE/lib/proto/protoToolExecute.py "$GALAXY_OUTPUT" "$GALAXY_OUTPUT_ID"
