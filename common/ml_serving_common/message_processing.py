import logging

import pika # type: ignore
from .config import Config # type: ignore
from .wrappers import RedisWrapper, RabbitWrapper
from .inference import PredictorBase

class MessageProcessor(object):
    def __init__(self, config: Config, predictor: PredictorBase):
        self.__logger = config.LOGGER
        self.__predictor = predictor
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

def runMessageProcessor(predictor: PredictorBase) -> None:
    config = Config()
    proc = MessageProcessor(config, predictor)
    proc.run()
