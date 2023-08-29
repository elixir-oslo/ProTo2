# From: https://github.com/syncthing/syncthing/blob/main/Dockerfile

ARG GOVERSION=1.20.7

FROM golang:$GOVERSION AS builder

WORKDIR /src

RUN SYNCTHING_SRC_URL=$(curl -X GET https://api.github.com/repos/syncthing/syncthing/releases/latest | sed -rn 's/^.*(https.*syncthing-source.*\.tar\.gz).*$/\1/p' | head -n 1) && \
    curl -fsSLo syncthing-source.tar.gz $SYNCTHING_SRC_URL && \
    tar xfzv syncthing-source.tar.gz syncthing

ENV CGO_ENABLED=0
ENV BUILD_HOST=syncthing.net
ENV BUILD_USER=docker

RUN cd syncthing && \
    go run build.go -no-upgrade build syncthing

FROM localhost/alpine-glibc-mambaforge

# EXPOSE 8384 22000/tcp 22000/udp 21027/udp

RUN apk update && \
    apk add --no-cache ca-certificates su-exec tzdata && \
    rm -rf /var/cache/apk/*

# VOLUME ["/var/syncthing"]
RUN mkdir /var/syncthing

COPY --from=builder /src/syncthing/syncthing /bin/syncthing
COPY --from=builder /src/syncthing/script/docker-entrypoint.sh /bin/entrypoint.sh

ENV HOME=/var/syncthing

HEALTHCHECK --interval=1m --timeout=10s \
  CMD nc -z 127.0.0.1 8384 || exit 1

ENV STGUIADDRESS=0.0.0.0:8384

#ENTRYPOINT ["/bin/entrypoint.sh", "/bin/syncthing", "-home", "/var/syncthing/config"]
CMD /bin/entrypoint.sh /bin/syncthing -home /var/syncthing/config & /bin/bash
