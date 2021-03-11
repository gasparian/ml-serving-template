FROM python:3.8

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get clean && apt-get update && \
    apt-get -y install --no-install-recommends \
        build-essential \
        software-properties-common \
        supervisor \
        && \
    rm -rf /var/lib/apt/lists/*

COPY ./consumers/fasttext/requirements.txt requirements.txt
RUN python3 -m pip --no-cache-dir install -r requirements.txt

COPY ./ml-serving ./ml-serving
WORKDIR /ml-serving
RUN python3 -m pip --no-cache-dir install .
WORKDIR /

RUN apt-get update \
    && apt-get purge -y \
       build-essential \
    && apt-get clean \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/cache/apt/*

###########################################################

COPY ./supervisord.conf /etc/supervisor/conf.d/supervisord.conf 
COPY ./consumers/fasttext ./consumers/fasttext

RUN chmod +x /consumers/fasttext/src/main_predictor.py && \
    chmod +x /consumers/fasttext/src/main_cache.py

EXPOSE 5000

ENTRYPOINT ["/usr/bin/supervisord"]
