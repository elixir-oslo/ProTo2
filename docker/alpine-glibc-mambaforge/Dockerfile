FROM jeanblanchard/alpine-glibc

RUN ln -sf /usr/glibc-compat/lib64/ld-linux-x86-64.so.2 /lib64/ld-linux-x86-64.so.2

ENV PATH /opt/mambaforge/bin:$PATH

RUN apk update && \
    apk add --no-cache curl bash procps && \
    rm -rf /var/cache/apk/*

WORKDIR /tmp/

RUN curl -fsSLo Mambaforge.sh https://github.com/conda-forge/miniforge/releases/download/4.12.0-3/Mambaforge-4.12.0-3-$(uname)-$(uname -m).sh && \
    sha256sum Mambaforge.sh && \
    echo "93d481e4f12dce9f2ffe46904dc8cf88485c7b27fc4d18dd8e900e2c3ab83f80  Mambaforge.sh" | sha256sum -c

RUN bash Mambaforge.sh -b -p /opt/mambaforge &&\
    ln -s /opt/mambaforge/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/mambaforge/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc && \
    find /opt/mambaforge/ -follow -type f -name '*.a' -delete && \
    find /opt/mambaforge/ -follow -type f -name '*.js.map' -delete && \
    conda clean -afy && \
    rm Mambaforge.sh && \
    find /opt/mambaforge -name __pycache__ -exec rm -rf {} \+

CMD ["/bin/bash"]
