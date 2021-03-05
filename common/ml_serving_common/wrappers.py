import logging
from typing import Any, Callable
from threading import Thread

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
        # NOTE: will delete asynchronously 
        # if the size of value is large enough
        self.__cache.unlink(key) 

class RabbitWrapper(object):
    def __init__(self, config: Config):
        self.__logger = config.logger
        self.__rabbit_host=config.rabbit_host
        self.__rabbit_port=config.rabbit_port
        self.__queue_name = config.queue_name
        self.__rabbit_ttl = config.rabbit_ttl
        self.__exchange_name = config.exchange_name
        self.__exchange_type = config.exchange_type
        self.__prefetch_count = config.prefetch_count
        self.__rabbit_heartbeat_timeout = config.rabbit_heartbeat_timeout
        self.__rabbit_blocked_connection_timeout = config.rabbit_blocked_connection_timeout
        self.__connection = self.__create_connection()
        self.__channel = self.__create_channel()

    def __create_connection(self) -> pika.BlockingConnection:
        return pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.__rabbit_host,
                port=self.__rabbit_port,
                blocked_connection_timeout=self.__rabbit_blocked_connection_timeout,
                heartbeat=self.__rabbit_heartbeat_timeout
            )
        )
        
    def __create_channel(self) -> pika.channel:
        return self.__connection.channel()
    
    def declare_queue(self):
        try:
            self.__connection.process_data_events()
        except:
            if self.__connection.is_closed:
                self.__connection = self.__create_connection()
            if self.__channel.is_closed:
                self.__channel = self.__create_channel()
        if self.__exchange_name:
            self.__channel.exchange_declare(
                exchange=self.__exchange_name, 
                exchange_type=self.__exchange_type
            )
        self.__channel.queue_declare(queue=self.__queue_name, durable=True)
    
    # NOTE: on why I used threads here https://github.com/pika/pika/issues/1104
    def consume(self, callback: Callable) -> None:
        def cb(ch, method, properties, body):
            t = Thread(target=callback, args=(properties, body,))
            t.daemon = True
            t.start()

            while t.is_alive():
                # self.__connection.process_data_events()
                self.__connection.sleep(0.1)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        self.__channel.basic_qos(prefetch_count=self.__prefetch_count)
        self.__channel.basic_consume(queue=self.__queue_name, on_message_callback=cb)
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

    def close_channel(self) -> None:
        self.__channel.close()

    def close_connection(self) -> None:
        self.__connection.close()
