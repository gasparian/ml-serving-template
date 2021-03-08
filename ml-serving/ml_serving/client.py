import time
import uuid
import pickle
from typing import Any, Optional

from .config import Config
from .wrappers import RedisWrapper, RabbitWrapper, RabbitRpcClient

class ServingClient(object):
    def __init__(self, config: Config):
        self.__pause = config.cache_pooling_timeout
        self.__timeout = int(round(float(config.rabbit_ttl)/1000))
        self.__cache = RedisWrapper(config)
        self.__cache_pubsub = self.__cache.get_pubsub()
        self.__cache_pubsub.psubscribe('__keyspace@*')
        self.rabbit = RabbitWrapper(config)

    def __get_key_from_event(self, msg) -> str:
        if msg["type"] != "pmessage":
            return ""
        if msg["data"].decode() != "expire":
            return ""
        return msg["channel"].decode().split(":")[-1]

    def get_answer(self, key: str) -> Any:
        value = self.__cache.withdraw(key)
        if value:
            return pickle.loads(value)
        return value

    def run_prediction(self, data: Any) -> str:
        key = str(uuid.uuid4())
        self.rabbit.produce(key, pickle.dumps(data))
        return key

    def close(self) -> None:
        self.rabbit.close_connection()

class ServingRpcClient(ServingClient):
    def __init__(self, config: Config):
       self.rabbit = RabbitRpcClient(config)

    def get_answer(self, key: str = "") -> Any:
        value = self.rabbit.wait_answer()
        if value:
            return pickle.loads(value)
        return value
 