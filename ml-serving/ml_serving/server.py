import abc
import logging
import pickle
from typing import Optional
from threading import Lock

import pika # type: ignore
from .config import Config # type: ignore
from .wrappers import RedisWrapper, RabbitWrapper, RabbitRPCServer
from .inference import PredictorBase

class ServingConsumerBase(abc.ABC):
    def __init__(self, config: Config, predictor: PredictorBase):
        self.logger = config.logger
        self.predictor = predictor
        self.mutex = Lock()

    @abc.abstractmethod
    def consume(self) -> None:
        pass

class ServingConsumer(ServingConsumerBase):
    def __init__(self, config: Config, predictor: PredictorBase):
        super().__init__(config, predictor)
        self.__queue = RabbitWrapper(config)
        self.__cache = RedisWrapper(config)

    def consume(self) -> None:
        def cb(properties: pika.spec.BasicProperties, body: bytes):
            self.mutex.acquire()
            try:
                prediction = self.predictor.predict(pickle.loads(body))
                key = properties.correlation_id
                self.__cache[key] = pickle.dumps(prediction)
                self.logger.info(f" [x] Message {key} processed!")
            finally:
                self.mutex.release()
        self.__queue.consume(cb)

class ServingRPCConsumer(ServingConsumer):
    def __init__(self, config: Config, predictor: PredictorBase):
        super().__init__(config, predictor)
        self.__queue = RabbitRPCServer(config)

    def consume(self) -> None:
        def cb(body: bytes) -> Optional[bytes]:
            self.mutex.acquire()
            try:
                prediction = self.predictor.predict(pickle.loads(body))
            finally:
                self.mutex.release()
            return pickle.dumps(prediction)
        self.__queue.consume(cb)