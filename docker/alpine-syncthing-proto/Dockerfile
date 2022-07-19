FROM alpine-mamba-syncthing

ENV PUID="1000"
ENV PGID="1000"
ENV PATH /opt/miniforge3/bin:$PATH

RUN apk update && \
    apk add --no-cache curl net-tools nano less git dropbear && \
    rm -rf /var/cache/apk/*

# time

RUN conda config --add channels defaults && \
    conda config --add channels bioconda && \
    conda config --add channels conda-forge && \
    mamba create -y -n proto2 python=3.7

RUN mamba install -y -n proto2 flask=1.1.2 itsdangerous=2.0.1 jinja2=3.0.3 werkzeug=2.0.3 bioblend gunicorn numpy rpy2 pycryptodome && \
    conda clean -afy

# NB: python > 3.7 breaks flask-mako
RUN mamba run -n proto2 pip install Mako==1.1.6 flask-mako==0.4 && \
    find /opt/mambaforge -name __pycache__ -exec rm -rf {} \+

ENV BASE=/opt/proto2

RUN git clone https://github.com/elixir-oslo/ProTo2.git $BASE

#COPY . $BASE
#COPY proto2 $BASE/proto2


RUN mkdir /etc/dropbear && \
    touch /var/log/wtmp && \
    echo -e '#!/bin/sh\nls -al' > /usr/local/bin/ll && \
    chmod a+x /usr/local/bin/ll

#RUN mkdir /data
#VOLUME /data

WORKDIR $BASE

ENV STGUIADDRESS=0.0.0.0:8384

# TEMPORARILY
RUN apk update && \
    apk add --no-cache sudo && \
    rm -rf /var/cache/apk/*

# CMD ["./run.sh"]
# CMD ["/bin/entrypoint.sh", "/bin/syncthing", "-home", "/var/syncthing/config& ./run.sh