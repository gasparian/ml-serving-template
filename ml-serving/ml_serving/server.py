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
    def __init__(self, config: Config, predictor: Optional[PredictorBase] = None):
        self.__rabbit = RabbitWrapper(config)
        self.logger = config.logger
        self.mutex = Lock()
        self.queue_name = config.queue_name
        if predictor:
            self.predictor = predictor

    def consume(self) -> None:
        self.__rabbit.consume(self.queue_name, self.callback)

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

    @abc.abstractmethod
    def callback(self):
        pass

class ServingPredictor(ServingConsumerBase):
    def __init__(self, config: Config, predictor: PredictorBase):
        super().__init__(config, predictor)
        self.__cache = RedisWrapper(config)

    def callback(self, ch, method, properties: pika.spec.BasicProperties, body: bytes) -> None:
        self.mutex.acquire()
        try:
            key = properties.correlation_id
            prediction = self.predictor.predict(pickle.loads(body))
            self.__cache[key] = pickle.dumps(prediction)
            self.logger.info(f" [x] Message {key} processed!")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except:
            self.logger.info(f" [-] failed to process message {key}")
        finally:
            self.mutex.release()

class ServingRpcPredictor(ServingConsumerBase):
    def callback(self, ch, method, properties: pika.spec.BasicProperties, body: bytes) -> bytes:
        prediction = None
        self.mutex.acquire()
        try:
            prediction = self.predictor.predict(pickle.loads(body))
            self.rpc_wrapper(ch, method, properties, pickle.dumps(prediction))
        except:
            self.logger.info(f" [-] failed to process message {key}")
        finally:
            self.mutex.release()

class ServingRpcCache(ServingConsumerBase):
    def __init__(self, config: Config):
        super().__init__(config)
        self.__cache = RedisWrapper(config)
        self.queue_name = config.cache_queue_name

    def callback(self, ch, method, properties: pika.spec.BasicProperties, body: bytes) -> None:
        try:
            key = properties.correlation_id
            value = self.__cache.withdraw(key)
            if not value:
                value = pickle.dumps(None)
            self.rpc_wrapper(ch, method, properties, value)
        except:
            self.logger.info(f" [-] failed to process message {key}")
