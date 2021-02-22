import os
import sys
import logging
from typing import Dict, Any, Callable

import redis
import pika # type: ignore
from .inference import PredictorMock as Predictor # type: ignore
# from inference import Predictor

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

class RedisWrapper(object):
    def __init__(self, redis_host: str, redis_port: str, ttl: int):
        self.__cache = redis.Redis(host=redis_host, port=int(redis_port))
        self.__ttl = ttl

    def __setitem__(self, key: Any, value: Any) -> None:
        self.__cache.set(key, value, ex=self.__ttl)

class RabbitWrapper(object):
    def __init__(self, rabbit_host: str, rabbit_port: str, prefetch: int, queue_name: str):
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=rabbit_host,
                port=rabbit_port
            )
        )
        self.__channel = connection.channel()
        self.__prefetch = prefetch
        self.__queue_name = queue_name
    
    def create_queue(self):
        self.__channel.queue_declare(queue=self.__queue_name, durable=True)
    
    def consume(self, callback: Callable) -> None:
        self.__channel.basic_qos(prefetch_count=self.__prefetch)
        self.__channel.basic_consume(queue=self.__queue_name, on_message_callback=callback)
        self.__channel.start_consuming()

class MessageProcessor(object):
    def __init__(self, config: Config):
        self.__logger = config.LOGGER
        self.__predictor = Predictor(config.MODEL_PATH)
        self.__rabbit = RabbitWrapper(config.RABBIT_HOST, config.RABBIT_PORT, config.PREFETCH_COUNT, config.QUEUE_NAME)
        self.__redis = RedisWrapper(config.REDIS_HOST, config.REDIS_PORT, config.REDIS_TTL)

    def __callback(self, ch: pika.channel.Channel, method: pika.spec.Basic.Deliver, properties: pika.spec.BasicProperties, body: bytes) -> None:
        prediction = self.__predictor.predict(body)
        key = properties.headers["X-Message-Id"]
        self.__redis[key] = prediction
        self.__logger.info(f" [x] Message {key} processed!")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    def run(self) -> None:
        self.__rabbit.create_queue()
        self.__logger.info(' [*] Waiting for messages. To exit press CTRL+C')
        self.__rabbit.consume(self.__callback)
