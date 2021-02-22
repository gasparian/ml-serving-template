import os
import time
import uuid

import ujson
import redis
import pika # type: ignore

rabbit_ttl = os.environ["RABBITMQ_TTL"]

redis_host, redis_port = os.environ["REDIS_ADDR"].split(":")
cache = redis.Redis(host=redis_host, port=int(redis_port))

host, port = os.environ["RABBITMQ_ADDR"].split(":")
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=host,
        port=port
    )
)
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)

message = {
    "Key": str(uuid.uuid4()),
    "Value": "Hello World!"
}
channel.basic_publish(
    exchange='',
    routing_key='task_queue',
    body=message["Value"].encode(),
    properties=pika.BasicProperties(
        delivery_mode=2,  # make message persistent
        expiration=rabbit_ttl,
        headers={"X-Message-Id": message["Key"]}
    ))
print(" [x] Sent %r" % message)
connection.close()

c = 0
item = None
while c < 60:
    item = cache.get(message["Key"])
    if item:
        break
    else:
        time.sleep(1)
    c += 1

if item:
    item = ujson.loads(item)

print("Got data from redis: %s" % item)
