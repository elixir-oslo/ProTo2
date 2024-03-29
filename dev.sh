#!/bin/sh

HERE=$(dirname $0)

cd $HERE

export PYTHONPATH=$PYTHONPATH:$HERE/lib

export FLASK_APP=proto2.flask_app:create_app
export FLASK_ENV=development

flask run -h 0.0.0.0 -p 5000 &

echo $! > flask.pid
cat flask.pid
trap 'kill $(cat flask.pid)' INT
wait
