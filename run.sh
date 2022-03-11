#!/bin/sh

HERE=$(dirname "$0")

cd "$HERE"

export PYTHONPATH=$PYTHONPATH:$HERE/lib

export FLASK_APP=proto2.flask_app
#export FLASK_ENV=development

export SCRIPT_NAME=$(python proto2/get_proxy_path.py)
echo $SCRIPT_NAME

#flask run -h 0.0.0.0 -p 5000 > flask.log 2>&1 &
gunicorn -b 0.0.0.0:5000 -p flask.pid --log-file flask.log --reload "$FLASK_APP:create_app()"

#echo $! > flask.pid
#cat flask.pid
#trap 'kill $(cat flask.pid)' INT
#wait
