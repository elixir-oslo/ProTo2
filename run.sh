#!/bin/sh

HERE=$(dirname $0)

cd $HERE

export PYTHONPATH=$PYTHONPATH:$HERE/lib

export FLASK_APP=proto2
export FLASK_ENV=development

flask run -h 0.0.0.0 -p 5000
