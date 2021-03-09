import abc
import logging
import pickle
from typing import Optional
from threading import Lock

import pika # type: ignore
from .config import Config # type: ignore
from .wrappers import RedisWrapper, RabbitWrapper, RabbitRpcServer
from .inference import PredictorBase

class ServingConsumerBase(abc.ABC):
    def __init__(self, config: Config, predictor: PredictorBase, queue: RabbitWrapper):
        self.__queue = queue
        self.logger = config.logger
        self.predictor = predictor
        self.mutex = Lock()

    def consume(self) -> None:
        self.__queue.consume(self.callback)

    @abc.abstractmethod
    def callback(self):
        pass

class ServingConsumer(ServingConsumerBase):
    def __init__(self, config: Config, predictor: PredictorBase, queue: RabbitWrapper):
        super().__init__(config, predictor, queue)
        self.__cache = RedisWrapper(config)

    def callback(self, properties: pika.spec.BasicProperties, body: bytes) -> None:
        self.mutex.acquire()
        try:
            prediction = self.predictor.predict(pickle.loads(body))
            key = properties.correlation_id
            self.__cache[key] = pickle.dumps(prediction)
            self.logger.info(f" [x] Message {key} processed!")
        finally:
            self.mutex.release()

class ServingRpcConsumer(ServingConsumerBase):
    def __init__(self, config: Config, predictor: PredictorBase, queue: RabbitRpcServer):
        super().__init__(config, predictor, queue)

    def callback(self, body: bytes) -> bytes:
        prediction = None
        self.mutex.acquire()
        try:
            prediction = self.predictor.predict(pickle.loads(body))
        finally:
            self.mutex.release()
        return pickle.dumps(prediction)
