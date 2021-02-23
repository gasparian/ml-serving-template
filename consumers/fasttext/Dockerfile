FROM python:3.8

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get clean && apt-get update && \
    apt-get -y install --no-install-recommends \
        build-essential \
        software-properties-common \
        && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN python3 -m pip --no-cache-dir install -r requirements.txt

RUN apt-get update \
    && apt-get purge -y \
       build-essential \
    && apt-get clean \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/cache/apt/*

###########################################################

COPY . .

EXPOSE 5000

ENTRYPOINT ["python3", "-m", "consumer"]
