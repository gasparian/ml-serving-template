import logging
from typing import Any, Callable

import redis
import pika # type: ignore
from .config import Config

class RedisWrapper(object):
    def __init__(self, config: Config):
        self.__cache = redis.Redis(host=config.REDIS_HOST, port=int(config.REDIS_PORT))
        self.__ttl = config.REDIS_TTL

    def __setitem__(self, key: str, value: Any) -> None:
        self.__cache.set(key, value, ex=self.__ttl)

    def __getitem__(self, key: str) -> Any:
        return self.__cache.get(key)

class RabbitWrapper(object):
    def __init__(self, config: Config):
        self.__connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=config.RABBIT_HOST,
                port=config.RABBIT_PORT
            )
        )
        self.__channel = self.__connection.channel()
        self.__prefetch = config.PREFETCH_COUNT
        self.__queue_name = config.QUEUE_NAME
        self.__rabbit_ttl = config.RABBIT_TTL
        self.__exchange_name = config.EXCHANGE_NAME
        self.__exchange_type = config.EXCHANGE_TYPE
    
    def declare_queue(self):
        if self.__exchange_name:
            self.__channel.exchange_declare(
                exchange=self.__exchange_name, 
                exchange_type=self.__exchange_type
            )
        self.__channel.queue_declare(queue=self.__queue_name, durable=True)
    
    def consume(self, callback: Callable) -> None:
        self.__channel.basic_qos(prefetch_count=self.__prefetch)
        self.__channel.basic_consume(queue=self.__queue_name, on_message_callback=callback)
        self.__channel.start_consuming()

    def produce(self, key: str, value: Any) -> None:
        self.__channel.basic_publish(
            exchange=self.__exchange_name,
            routing_key=self.__queue_name,
            body=value, # must be bytes
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
                expiration=self.__rabbit_ttl,
                headers={"X-Message-Id": key}
            ))

    def close(self) -> None:
        self.__connection.close()
