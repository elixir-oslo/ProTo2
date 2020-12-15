FROM continuumio/miniconda3:4.8.2

ENV BASE=/opt/proto
#ENV PATH=$PATH:/usr/local/bin

COPY . $BASE
#COPY proto2 $BASE/proto2

RUN apt-get update
RUN apt-get install -y procps net-tools time curl
#RUN apt-get upgrade -y
#RUN apt-get clean

#RUN conda update -n base -c defaults conda

RUN conda config --add channels bioconda
RUN conda config --add channels conda-forge

RUN conda install flask=1.1.2 bioblend
#RUN conda clean -a

RUN pip install flask-mako

#RUN mkdir /data
#VOLUME /data

WORKDIR $BASE

CMD ["./run.sh"]
