import time
import uuid
import pickle
from typing import Any, Optional

from .config import Config
from .wrappers import RedisWrapper, RabbitWrapper

class ServingClient(object):
    def __init__(self, config: Config):
        self.__pause = config.cache_pooling_timeout
        self.__timeout = int(round(float(config.rabbit_ttl)/1000))
        self.__cache = RedisWrapper(config)
        self.__cache_pubsub = self.__cache.get_pubsub()
        self.__cache_pubsub.psubscribe('__keyspace@*')
        self.__rabbit = RabbitWrapper(config)

    def __get_key_from_event(self, msg) -> str:
        if msg["type"] != "pmessage":
            return ""
        if msg["data"].decode() != "expire":
            return ""
        return msg["channel"].decode().split(":")[-1]

    def run_prediction(self, data: Any) -> str:
        key = str(uuid.uuid4())
        self.__rabbit.produce(key, pickle.dumps(data))
        return key

    # TODO: rewrite with rabbit
    def wait_answer(self, key: str) -> Any:
        total_time = 0.0
        value = None
        time.sleep(self.__pause)
        while total_time < self.__timeout:
            total_time += self.__pause
            message = self.__cache_pubsub.get_message()
            if message:
                msg_key = self.__get_key_from_event(message)
                if msg_key and (msg_key == key):
                    value = self.__cache.withdraw(key)
                    break
            time.sleep(self.__pause)
        if value:
            return pickle.loads(value)
        return value

    def get_answer(self, key: str) -> Any:
        value = self.__cache.withdraw(key)
        if value:
            return pickle.loads(value)
        return value

    def close(self):
        self.__rabbit.close_connection()
