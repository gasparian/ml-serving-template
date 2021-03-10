import abc
import logging
import pickle
from typing import Optional
from threading import Lock

import pika # type: ignore
from .config import Config # type: ignore
from .wrappers import RedisWrapper, RabbitWrapper
from .inference import PredictorBase

class ServingConsumerBase(abc.ABC):
    def __init__(self, config: Config, predictor: PredictorBase):
        self.__rabbit = RabbitWrapper(config)
        self.logger = config.logger
        self.predictor = predictor
        self.mutex = Lock()

    def consume(self) -> None:
        self.__rabbit.consume(self.callback)

    @abc.abstractmethod
    def callback(self):
        pass

class ServingPredictor(ServingConsumerBase):
    def __init__(self, config: Config, predictor: PredictorBase):
        super().__init__(config, predictor, rabbit)
        self.__cache = RedisWrapper(config)

    def callback(self, ch, method, properties: pika.spec.BasicProperties, body: bytes) -> None:
        self.mutex.acquire()
        try:
            prediction = self.predictor.predict(pickle.loads(body))
            self.__cache[key] = pickle.dumps(prediction)
            self.logger.info(f" [x] Message {key} processed!")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        finally:
            self.mutex.release()

class ServingRpcPredictor(ServingConsumerBase):
    def rpc_wrapper(self, ch, method, properties: pika.spec.BasicProperties, body: bytes):
        ch.basic_publish(
            exchange='',
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(
                correlation_id=properties.correlation_id
            ),
            body=body
        )
        key = properties.correlation_id
        self.logger.info(f" [x] Message {key} processed!")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def callback(self, ch, method, properties: pika.spec.BasicProperties, body: bytes) -> bytes:
        prediction = None
        self.mutex.acquire()
        try:
            prediction = self.predictor.predict(pickle.loads(body))
            self.rpc_wrapper(ch, method, properties, pickle.dumps(prediction))
        finally:
            self.mutex.release()

class ServingCache(ServingRpcPredictor):
    def __init__(self, config: Config, predictor: PredictorBase):
        super().__init__(config, predictor, rabbit)
        self.__cache = RedisWrapper(config)

    def __get_from_cache(self, body: bytes) -> bytes:
        key = body.decode("utf-8")
        value = self.__cache.withdraw(key)
        return value

    def callback(self, ch, method, properties: pika.spec.BasicProperties, body: bytes) -> None:
        key = properties.correlation_id
        prediction = self.__get_from_cache(key)
        if not prediction:
            prediction = pickle.dumps(None)
        self.rpc_wrapper(ch, method, properties, prediction)
