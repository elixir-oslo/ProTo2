#!/bin/sh

HERE=$(dirname $0)


cd $HERE/../proto2

export FLASK_ENV=development

flask run -h 0.0.0.0 -p 5000
