import os
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%d/%b/%Y %H:%M:%S",
    stream=sys.stdout
)

class Config(object):
    LOGGER = logging.getLogger()
    REDIS_TTL= int(os.environ["REDIS_TTL"]) 
    PREFETCH_COUNT = int(os.environ["PREFETCH_COUNT"])
    REDIS_HOST, REDIS_PORT = os.environ["REDIS_ADDR"].split(":")
    RABBIT_HOST, RABBIT_PORT = os.environ["RABBITMQ_ADDR"].split(":")
    MODEL_PATH = os.environ["MODEL_PATH"]
    QUEUE_NAME = os.environ["QUEUE_NAME"]
    EXCHANGE_TYPE = os.environ["EXCHANGE_TYPE"]
    EXCHANGE_NAME = os.environ["EXCHANGE_NAME"]
    RABBIT_TTL = os.environ["RABBITMQ_TTL"]
