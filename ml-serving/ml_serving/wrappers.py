import logging
import random
from typing import Any, Callable, Optional
from threading import Thread

import redis
import pika # type: ignore
from .config import Config

class RedisWrapper(object):
    def __init__(self, config: Config):
        # NOTE: you can switch to the Redis cluster if you're using one
        # https://github.com/Grokzen/redis-py-cluster
        self.__redis = redis.Redis(
            host=config.redis_nodes[0]["host"], 
            port=int(config.redis_nodes[0]["port"])
        )
        self.__ttl = config.redis_ttl

    def __setitem__(self, key: str, value: Any) -> None:
        self.__redis.set(key, value, ex=self.__ttl)

    def __getitem__(self, key: str) -> Any:
        return self.__redis.get(key)

    def get_pubsub(self):
        return self.__redis.pubsub()

    def delete(self, key: str):
        # NOTE: will delete asynchronously 
        # if the size of a value is large enough
        self.__redis.unlink(key) 

    def withdraw(self, key: str) -> Any:
        value = self.__getitem__(key)
        if value:
            self.delete(key)
        return value

class RabbitWrapper(object):
    def __init__(self, config: Config):
        self.logger = config.logger
        self.__rabbit_nodes = config.rabbit_nodes
        self.__exchange_type = config.exchange_type
        self.__rabbit_heartbeat_timeout = config.rabbit_heartbeat_timeout
        self.__rabbit_blocked_connection_timeout = config.rabbit_blocked_connection_timeout
        self.queue_name = config.queue_name
        self.rabbit_ttl = config.rabbit_ttl
        self.exchange_name = config.exchange_name
        self.prefetch_count = config.prefetch_count
        self.connection = self.__create_connection()
        self.channel = self.__create_channel()

    def __create_connection(self) -> pika.BlockingConnection:
        random.shuffle(self.__rabbit_nodes)
        return pika.BlockingConnection([
            pika.ConnectionParameters(
                host=address["host"],
                port=int(address["port"]),
                blocked_connection_timeout=self.__rabbit_blocked_connection_timeout,
                heartbeat=self.__rabbit_heartbeat_timeout
            )
            for address in self.__rabbit_nodes
        ])
        
    def __create_channel(self) -> pika.channel:
        return self.connection.channel()
    
    def declare_queue(self) -> bool:
        recreated = False
        try:
            self.connection.process_data_events()
        except:
            if self.connection.is_closed:
                self.connection = self.__create_connection()
            if self.channel.is_closed:
                self.channel = self.__create_channel()
                recreated = True
        if self.exchange_name:
            self.channel.exchange_declare(
                exchange=self.exchange_name, 
                exchange_type=self.__exchange_type
            )
        self.channel.queue_declare(queue=self.queue_name, durable=True)
        return recreated
    
    def start_consuming(self, callback: Callable) -> None:
        self.channel.basic_qos(prefetch_count=self.prefetch_count)
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=callback)
        self.channel.start_consuming()

    # NOTE: https://pika.readthedocs.io/en/stable/examples/blocking_consume_recover_multiple_hosts.html
    def consume(self, callback: Callable) -> None:
        while True:
            try:
                self.declare_queue()
                try:
                    self.logger.info(' [*] Start consuming... Waiting for messages. To exit press CTRL+C')
                    self.start_consuming(callback)
                except KeyboardInterrupt:
                    self.logger.info("Stop consuming...")
                    self.channel.stop_consuming()
                    self.close_connection()
                    break
            except pika.exceptions.ConnectionClosedByBroker:
                continue
            except pika.exceptions.AMQPChannelError as err:
                self.logger.error("Caught a channel error: {}, stopping...".format(err))
                break
            except pika.exceptions.AMQPConnectionError:
                self.logger.error("Connection was closed, retrying...")
                continue 

    def produce(self, key: str, value: bytes) -> None:
        self.declare_queue()
        self.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=self.queue_name,
            body=value, # must be bytes
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
                expiration=self.rabbit_ttl,
                correlation_id=key
            )
        )

    def close_channel(self) -> None:
        self.channel.close()

    def close_connection(self) -> None:
        self.connection.close()

# NOTE: basic logic taken from here: https://www.rabbitmq.com/tutorials/tutorial-six-python.html
class RabbitRpcClient(RabbitWrapper):
    def __init__(self, config: Config):
        super().__init__(config)
        self.__init_callback_queue()

    def __init_callback_queue(self):
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.__callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.__callback_queue,
            on_message_callback=self.__on_response,
            auto_ack=True
        )

    def __on_response(self, ch, method, props, body):
        if self.__corr_id == props.correlation_id:
            self.__response = body

    def blocking_produce(self, key: str, value: Optional[bytes]) -> None:
        channel_recreated = self.declare_queue()
        if channel_recreated:
            self.__init_callback_queue()
        self.__response = None
        self.__corr_id = key
        self.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=self.queue_name,
            properties=pika.BasicProperties(
                reply_to=self.__callback_queue,
                expiration=self.rabbit_ttl,
                correlation_id=self.__corr_id,
            ),
            body=value if value else b""
        )

        while self.__response is None:
            self.connection.process_data_events()
            self.connection.sleep(0.05)
        return self.__response
