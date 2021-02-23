FROM ubuntu:16.04

RUN export DEBIAN_FRONTEND=noninteractive \
    APT_INSTALL="apt-get install -y --no-install-recommends" && \
    apt-get update && \
    $APT_INSTALL \
        build-essential \
        ca-certificates \
        cmake \
        wget \
        git \
        vim \
        unzip \
        && \
    $APT_INSTALL \
    software-properties-common \
        && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    $APT_INSTALL \
        python3.6 \
        python3.6-dev

RUN wget -O ~/get-pip.py \
        https://bootstrap.pypa.io/get-pip.py && \
    python3.6 ~/get-pip.py && \
    ln -s /usr/bin/python3.6 /usr/local/bin/python3 && \
    ln -s /usr/bin/python3.6 /usr/local/bin/python && \
    ldconfig && \
    apt-get clean && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/cache/apt/*

RUN python -m pip --no-cache-dir install \
        future>=0.17.1 \
        six==1.10.0 \
        mock==3.0.5 \
        requests==2.22.0 \
        jmespath==0.9.0 \
        numpy==1.15.4 \
        scipy==1.1.0 \
        scikit-learn==0.23.1 \
        nltk==3.4 \
        fasttext==0.9.1 \
        gunicorn==19.7.1 \
        python-dateutil==2.6.0 \
        flask==1.0.2

RUN python3 -m nltk.downloader stopwords

RUN apt-get update \
    && apt-get purge -y \
       build-essential \
    && apt-get clean \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/cache/apt/*

###########################################################

COPY . /app

RUN chmod +x /app/run_app.sh

EXPOSE 8000

WORKDIR /app
ENTRYPOINT ["./run_app.sh"]

# FROM python:3.8

# ARG DEBIAN_FRONTEND=noninteractive

# RUN apt-get clean && apt-get update && \
#     apt-get -y install --no-install-recommends \
#         build-essential \
#         libev-dev \
#         ca-certificates \
#         cmake \
#         wget \
#         git \
#         vim \
#         unzip \
#         software-properties-common \
#         && \
#     rm -rf /var/lib/apt/lists/*

# RUN python3 -m pip --no-cache-dir install \
#     requests==2.22.0 \
#     numpy==1.15.4 \
#     fasttext==0.9.1 \
#     ujson==4.0.0 \
#     bjoern==3.1.0

# RUN python3 -m pip --no-cache-dir install \
#     -v --no-binary :all: falcon==2.0.0

# # TO DO: join with other python libs installation later
# RUN python3 -m pip --no-cache-dir install \
#     pika==0.9.5 \
#     redis==3.5.3

# RUN apt-get update \
#     && apt-get purge -y \
#        build-essential \
#     && apt-get clean \
#     && apt-get autoremove -y \
#     && rm -rf /var/lib/apt/lists/* /tmp/* /var/cache/apt/*

# ###########################################################

# COPY . .

# EXPOSE 5000

# WORKDIR /src

# ENTRYPOINT ["python3", "./wsgi.py"]