FROM alpine-mamba-syncthing

ENV PUID="1000"
ENV PGID="1000"
ENV PATH /opt/miniforge3/bin:$PATH

RUN apk update && \
    apk add --no-cache curl net-tools nano less git dropbear && \
    rm -rf /var/cache/apk/*

ENV BASE=/opt/proto2

RUN git clone https://github.com/elixir-oslo/ProTo2.git $BASE

WORKDIR $BASE

RUN conda create --name proto2 --file conda-linux-64.lock && \
    conda clean -afy

# Temporarily
RUN git pull

RUN conda run -n proto2 poetry install --no-root

RUN mkdir /etc/dropbear && \
    touch /var/log/wtmp && \
    echo -e '#!/bin/sh\nls -al' > /usr/local/bin/ll && \
    chmod a+x /usr/local/bin/ll

ENV STGUIADDRESS=0.0.0.0:8384

# TEMPORARILY
RUN apk update && \
    apk add --no-cache sudo && \
    rm -rf /var/cache/apk/*

# Temporarily
RUN git pull

# CMD ["./run.sh"]
# CMD ["/bin/entrypoint.sh", "/bin/syncthing", "-home", "/var/syncthing/config& ./run.sh
