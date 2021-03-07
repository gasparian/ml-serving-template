import logging
import pickle
from threading import Lock

import pika # type: ignore
from .config import Config # type: ignore
from .wrappers import RedisWrapper, RabbitWrapper
from .inference import PredictorBase

class ServingConsumer(object):
    def __init__(self, config: Config, predictor: PredictorBase):
        self.__logger = config.logger
        self.__predictor = predictor
        self.__queue = RabbitWrapper(config)
        self.__cache = RedisWrapper(config)
        self.__mutex = Lock()

    def __callback(self, properties: pika.spec.BasicProperties, body: bytes) -> None:
        self.__mutex.acquire()
        try:
            prediction = self.__predictor.predict(pickle.loads(body))
            key = properties.headers["X-Message-Id"]
            self.__cache[key] = pickle.dumps(prediction)
            self.__logger.info(f" [x] Message {key} processed!")
        finally:
            self.__mutex.release()
    
    def consume(self) -> None:
        self.__queue.consume(self.__callback)

def start_consume_messages(config: Config, predictor: PredictorBase) -> None:
    proc = ServingConsumer(config, predictor)
    proc.consume()