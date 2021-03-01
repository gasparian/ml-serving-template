import time
import uuid
import pickle
from typing import Any

from .config import Config
from .wrappers import RedisWrapper, RabbitWrapper

class ServingClient(object):
    def __init__(self, config: Config):
        self.__pause = 0.25
        self.__logger = config.logger
        self.__timeout = config.rabbit_ttl
        self.__cache = RedisWrapper(config)
        self.__rabbit = RabbitWrapper(config)
        self.__rabbit.declare_queue()

    def __get_answer(self, key: str, value: bytes) -> bytes:
        self.__rabbit.produce(key, value)
        total_time = 0.0
        item = b""
        self.__logger.debug(f"[Pooling cache] Message: {key}")
        while total_time < self.timeout:
            item = cache[message["Key"]]
            if item:
                return item
            else:
                time.sleep(self.pause)
        self.__logger.debug(f"[Pooling cache] Got result from cache: {item}")
        return item
            
    def run_prediction(self, data: Any) -> Any:
        key = str(uuid.uuid4())
        answer = self.__get_answer(key, pickle.dumps(data))
        return pickle.loads(answer)

    def close(self):
        self.__rabbit.close()
