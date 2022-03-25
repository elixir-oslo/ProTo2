#!/bin/bash

if [ "$1" == "build" ]; then
  docker build -t proto2.norgene.no/proto2-test .
elif [ "$1" == "run" ]; then
  docker run -it --rm -p 127.0.0.1:5001:5000 --add-host localhost.norgene.no:192.168.65.2 proto2-test
fi
