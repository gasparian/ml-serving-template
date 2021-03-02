import time
import uuid
import pickle
from typing import Any

from .config import Config
from .wrappers import RedisWrapper, RabbitWrapper

class ServingClient(object):
    def __init__(self, config: Config):
        self.__pause = config.cache_pooling_timeout
        self.__timeout = config.rabbit_ttl
        self.__cache = RedisWrapper(config)
        self.__cache_pubsub = self.__cache.get_pubsub()
        self.__cache_pubsub.psubscribe('__keyspace@0__:*')
        self.__rabbit = RabbitWrapper(config)
        self.__rabbit.declare_queue()

    def __get_key_from_event(self, msg) -> str:
        if msg["type"] != "pmessage":
            return ""
        return msg["channel"].decode().split("__:")[-1]

    def __get_answer(self, key: str) -> bytes:
        total_time = 0.0
        item = b""
        time.sleep(self.__pause)
        while total_time < self.__timeout:
            message = self.__cache_pubsub.get_message()
            if message:
                msg_key = self.__get_key_from_event(message)
                if msg_key and (msg_key == key):
                    item = self.__cache[key]
                    break
            else:
                time.sleep(self.__pause)
        return item
            
    def run_prediction(self, data: Any) -> Any:
        key = str(uuid.uuid4())
        self.__rabbit.produce(key, pickle.dumps(data))
        answer = self.__get_answer(key)
        return pickle.loads(answer)

    def close(self):
        self.__rabbit.close()
