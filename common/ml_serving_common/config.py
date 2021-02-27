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
    def __init__(self):
        self.LOGGER = logging.getLogger()
        self.REDIS_TTL= int(os.environ["REDIS_TTL"]) 
        self.PREFETCH_COUNT = int(os.environ["PREFETCH_COUNT"])
        self.REDIS_HOST, self.REDIS_PORT = os.environ["REDIS_ADDR"].split(":")
        self.RABBIT_HOST, self.RABBIT_PORT = os.environ["RABBITMQ_ADDR"].split(":")
        self.QUEUE_NAME = os.environ["QUEUE_NAME"]
        self.EXCHANGE_TYPE = os.environ["EXCHANGE_TYPE"]
        self.EXCHANGE_NAME = os.environ["EXCHANGE_NAME"]
        self.RABBIT_TTL = os.environ["RABBITMQ_TTL"]
