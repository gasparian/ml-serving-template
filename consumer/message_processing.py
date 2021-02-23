import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import logging
import pika # type: ignore

from common import Config # type: ignore
from common.wrappers import RedisWrapper, RabbitWrapper
from .inference import PredictorMock as Predictor # type: ignore
# from inference import Predictor

class MessageProcessor(object):
    def __init__(self, config: Config):
        self.__logger = config.LOGGER
        self.__predictor = Predictor(config.MODEL_PATH)
        self.__queue = RabbitWrapper(config)
        self.__cache = RedisWrapper(config)

    def __callback(self, ch: pika.channel.Channel, method: pika.spec.Basic.Deliver, properties: pika.spec.BasicProperties, body: bytes) -> None:
        prediction = self.__predictor.predict(body)
        key = properties.headers["X-Message-Id"]
        self.__cache[key] = prediction
        self.__logger.info(f" [x] Message {key} processed!")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    def run(self) -> None:
        self.__queue.declare_queue()
        self.__logger.info(' [*] Waiting for messages. To exit press CTRL+C')
        self.__queue.consume(self.__callback)
