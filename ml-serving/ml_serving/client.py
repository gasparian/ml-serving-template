import time
import uuid
import pickle
from typing import Any, Optional

from .config import Config
from .wrappers import RabbitRpcClient

class ServingClient(object):
    def __init__(self, config: Config):
        self.__queue_name = config.queue_name
        self.__cache_queue_name = config.cache_queue_name
        self.__timeout = int(round(float(config.rabbit_ttl)/1000))
        self.__rabbit = RabbitRpcClient(config)

    def predict_async(self, data: Any) -> str:
        key = str(uuid.uuid4())
        self.__rabbit.produce(self.__queue_name, key, pickle.dumps(data))
        return key

    def get_result(self, key: str) -> Any:
        value = self.__rabbit.blocking_produce(self.__cache_queue_name, key)
        if value:
            return pickle.loads(value)
        return value

    def predict_sync(self, data: Any) -> Any:
        key = str(uuid.uuid4())
        value = self.__rabbit.blocking_produce(self.__queue_name, key, pickle.dumps(data))
        if value:
            return pickle.loads(value)
        return value

    def close(self) -> None:
        self.__rabbit.close_connection()
 