#FROM continuumio/miniconda3:4.10.3

FROM elixir-oslo/syncthing-alpine-glibc

#FROM condaforge/mambaforge
#FROM alpine-glibc

#RUN apk add libaio libnsl libc6-compat

ENV PATH /opt/miniforge3/bin:$PATH

RUN apk update && apk add curl bash procps net-tools curl nano libaio libnsl libc6-compat
# time

RUN curl -fsSLo Miniforge3.sh https://github.com/conda-forge/miniforge/releases/download/4.10.3-5/Miniforge3-4.10.3-5-$(uname)-$(uname -m).sh

RUN sha256sum Miniforge3.sh

RUN echo "5f143112b6c9533c550b447cc01f7313a86b6b88b92632791bcb4320e57f9af6  Miniforge3.sh" | sha256sum -c

RUN bash Miniforge3.sh -b -p /opt/miniforge3 &&\
    ln -s /lib64/* /lib &&\
    ln -s /opt/miniforge3/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/miniforge3/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc && \
    find /opt/miniforge3/ -follow -type f -name '*.a' -delete && \
    find /opt/miniforge3/ -follow -type f -name '*.js.map' -delete && \
    /opt/miniforge3/bin/conda clean -afy

CMD ["/bin/bash"]

#RUN apt-get --allow-releaseinfo-change update
#RUN apt-get install -y procps net-tools time curl nano
#RUN apt-get upgrade -y
#RUN apt-get clean

#RUN conda update -n base -c defaults conda

RUN conda config --add channels defaults
RUN conda config --add channels bioconda
RUN conda config --add channels conda-forge
#RUN conda config --append channels bioconda

#RUN conda create -n proto2 python=3.7
RUN mamba create -y -n proto2 python=3.7

# Make RUN commands use the new environment:
#SHELL ["/bin/bash", "--login", "-c"]
#RUN mamba init bash
#RUN echo "mamba activate proto2" >> ~/.bashrc

#RUN conda install flask=1.1.2 itsdangerous=2.0.1 jinja2=3.0.3 bioblend gunicorn numpy r-base=3.6.3 rpy2
RUN mamba install -y -n proto2 flask=1.1.2 itsdangerous=2.0.1 jinja2=3.0.3 werkzeug=2.0.3 bioblend gunicorn numpy rpy2 pycryptodome

#RUN conda clean -a

# NB: python > 3.7 breaks flask-mako
RUN mamba run -n proto2 pip install Mako==1.1.6 flask-mako==0.4


ENV BASE=/opt/proto
#ENV PATH=$PATH:/usr/local/bin

COPY . $BASE
#COPY proto2 $BASE/proto2

#RUN mkdir /data
#VOLUME /data

WORKDIR $BASE


CMD ["./run.sh"]
