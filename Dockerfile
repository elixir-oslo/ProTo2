FROM continuumio/miniconda3:4.10.3

RUN apt-get --allow-releaseinfo-change update
RUN apt-get install -y procps net-tools time curl nano
#RUN apt-get upgrade -y
#RUN apt-get clean

#RUN conda update -n base -c defaults conda

RUN conda config --add channels bioconda
RUN conda config --add channels conda-forge

RUN conda install python=3.7 flask=1.1.2 itsdangerous=2.0.1 bioblend gunicorn numpy rpy2
#RUN conda clean -a

# NB: python > 3.7 breaks flask-mako
RUN pip install Mako==1.1.6 flask-mako==0.4


ENV BASE=/opt/proto
#ENV PATH=$PATH:/usr/local/bin

COPY . $BASE
#COPY proto2 $BASE/proto2

#RUN mkdir /data
#VOLUME /data

WORKDIR $BASE


CMD ["./run.sh"]
