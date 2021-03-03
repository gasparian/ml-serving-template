import logging
from typing import Any, Callable

import redis
import pika # type: ignore
from .config import Config

class RedisWrapper(object):
    def __init__(self, config: Config):
        self.__cache = redis.Redis(host=config.redis_host, port=config.redis_port)
        self.__ttl = config.redis_ttl

    def __setitem__(self, key: str, value: Any) -> None:
        self.__cache.set(key, value, ex=self.__ttl)

    def __getitem__(self, key: str) -> Any:
        return self.__cache.get(key)

    def get_pubsub(self):
        return self.__cache.pubsub()

    def delete(self, key: str):
        self.__cache.unlink(key) 

class RabbitWrapper(object):
    def __init__(self, config: Config):
        self.__connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=config.rabbit_host,
                port=config.rabbit_port
            )
        )
        self.__channel = self.__connection.channel()
        self.__prefetch = config.prefetch_count
        self.__queue_name = config.queue_name
        self.__rabbit_ttl = config.rabbit_ttl
        self.__exchange_name = config.exchange_name
        self.__exchange_type = config.exchange_type
    
    def declare_queue(self):
        if self.__exchange_name:
            self.__channel.exchange_declare(
                exchange=self.__exchange_name, 
                exchange_type=self.__exchange_type
            )
        self.__channel.queue_declare(queue=self.__queue_name, durable=True)
    
    # TODO: get rid of error missed heartbeats from client, timeout: 60s
    # https://github.com/pika/pika/issues/1104
    def consume(self, callback: Callable) -> None:
        self.__channel.basic_qos(prefetch_count=self.__prefetch)
        self.__channel.basic_consume(queue=self.__queue_name, on_message_callback=callback)
        self.__channel.start_consuming()

    def produce(self, key: str, value: bytes) -> None:
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
