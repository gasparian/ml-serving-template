import abc
import logging
import pickle
from typing import Optional

import pika # type: ignore
from pika.adapters.blocking_connection import BlockingChannel # type: ignore
from .config import Config # type: ignore
from .wrappers import RedisWrapper, RabbitWrapper
from .inference import PredictorBase

class ServingConsumerBase(abc.ABC):
    def __init__(self, config: Config, predictor: Optional[PredictorBase] = None):
        self.__rabbit = RabbitWrapper(config)
        self.queue_name = config.queue_name
        self.predictor = predictor

    def consume(self) -> None:
        self.__rabbit.consume(self.queue_name, self.callback)

    def rpc_wrapper(self, ch: BlockingChannel, method: pika.spec.Basic.Deliver, properties: pika.spec.BasicProperties, body: bytes):
        ch.basic_publish(
            exchange='',
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(
                correlation_id=properties.correlation_id
            ),
            body=body
        )

    @abc.abstractmethod
    def callback(self):
        pass

class ServingPredictor(ServingConsumerBase):
    def __init__(self, config: Config, predictor: PredictorBase):
        super().__init__(config, predictor)
        self.__cache = RedisWrapper(config)

    def callback(self, ch: BlockingChannel, method: pika.spec.Basic.Deliver, properties: pika.spec.BasicProperties, body: bytes) -> None:
        key = properties.correlation_id
        prediction = self.predictor.predict(pickle.loads(body))
        self.__cache[key] = pickle.dumps(prediction)

class ServingRpcPredictor(ServingConsumerBase):
    def callback(self, ch: BlockingChannel, method: pika.spec.Basic.Deliver, properties: pika.spec.BasicProperties, body: bytes) -> bytes:
        prediction = None
        prediction = self.predictor.predict(pickle.loads(body))
        self.rpc_wrapper(ch, method, properties, pickle.dumps(prediction))

class ServingRpcCache(ServingConsumerBase):
    def __init__(self, config: Config):
        super().__init__(config)
        self.__cache = RedisWrapper(config)
        self.queue_name = config.cache_queue_name

    def callback(self, ch: BlockingChannel, method: pika.spec.Basic.Deliver, properties: pika.spec.BasicProperties, body: bytes) -> None:
        key = properties.correlation_id
        value = self.__cache.withdraw(key)
        if not value:
            value = pickle.dumps(None)
        self.rpc_wrapper(ch, method, properties, value)
