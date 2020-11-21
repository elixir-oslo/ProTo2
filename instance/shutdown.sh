#!/bin/bash

HERE=$(dirname $0)
PID=$HERE/../flask.pid

sleep 2
kill $(cat $PID)
