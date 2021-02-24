FROM python:3.7

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get clean && apt-get update && \
    apt-get -y install --no-install-recommends \
        build-essential \
        libev-dev \
        ca-certificates \
        cmake \
        wget \
        git \
        vim \
        unzip \
        software-properties-common \
        && \
    rm -rf /var/lib/apt/lists/*

COPY ./producers/short-texts-clustering/requirements.txt requirements.txt
RUN python3 -m pip --no-cache-dir install -r requirements.txt

RUN python3 -m nltk.downloader stopwords

RUN python3 -m pip --no-cache-dir install \
    -v --no-binary :all: falcon==2.0.0

RUN apt-get update \
    && apt-get purge -y \
       build-essential \
    && apt-get clean \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/cache/apt/*

###########################################################

COPY ./common ./common
COPY ./producers/short-texts-clustering ./producers/short-texts-clustering

EXPOSE 5000

WORKDIR /producers/short-texts-clustering/src

# ENTRYPOINT ["python3", "./producers/short-texts-clustering/src/wsgi.py"]
ENTRYPOINT [ "bash" ]
