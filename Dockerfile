FROM python:3.8

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get clean && apt-get update && \
    apt-get -y install --no-install-recommends \
        build-essential \
        software-properties-common \
        && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m pip --no-cache-dir install \
    requests==2.22.0 \
    numpy==1.15.4 \
    fasttext==0.9.1 \
    pika==1.2.0 \
    redis==3.5.3 \
    ujson==4.0.0

RUN apt-get update \
    && apt-get purge -y \
       build-essential \
    && apt-get clean \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/cache/apt/*

###########################################################

COPY . .

EXPOSE 5000

ENTRYPOINT ["python3", "-m", "app"]
