import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

import os
import time
import uuid

import ujson
import redis
import pika # type: ignore

from common import Config # type: ignore
from common.wrappers import RedisWrapper, RabbitWrapper

count = 1
if len(sys.argv) == 2 and sys.argv[1]:
    count = int(sys.argv[1])

config = Config()
redis = RedisWrapper(config)
rabbit = RabbitWrapper(config)

rabbit.declare_queue()

message = {
    "Key": str(uuid.uuid4()),
    "Value": "Hello World!"
}

for i in range(count):
    rabbit.produce(message["Key"], message["Value"].encode())
    time.sleep(0.25)

    print(f" [{i}] Sent {message}")

    c = 0
    item = None
    while c < 2:
        item = redis[message["Key"]]
        if item:
            break
        else:
            time.sleep(1)
        c += 1
    
    if item:
        item = ujson.loads(item)
    else:
        sys.exit(1)
    
    print(f"[{i}] Got data from redis: {item}")

rabbit.close()
