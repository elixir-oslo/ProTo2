#!/bin/sh

HERE=$(dirname "$0")

cd "$HERE"

export PYTHONPATH=$PYTHONPATH:$HERE/lib

export FLASK_APP=proto2
#export FLASK_ENV=development

flask run -h 0.0.0.0 -p 5000 > flask.log 2>&1 &

echo $! > flask.pid
cat flask.pid
trap 'kill $(cat flask.pid)' INT
wait
