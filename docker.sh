#!/bin/bash

if [ "$1" == "build" ]; then
  docker build -t alpine-glibc-mambaforge docker/alpine-glibc-mambaforge
  docker build -t alpine-mamba-syncthing docker/alpine-mamba-syncthing
  docker build -t alpine-syncthing-proto docker/alpine-syncthing-proto
#  docker build -t proto2.norgene.no/proto2-test .
elif [ "$1" == "run" ]; then
#  docker run -it --rm -p 127.0.0.1:5001:5000 --add-host localhost.norgene.no:192.168.65.2 proto2-test
  docker run -it --rm -p 5000:5000 -p 2222:2222 -p  22000:22000/tcp -p 22000:22000/udp 21027:21027/udp alpine-syncthing-proto
fi
