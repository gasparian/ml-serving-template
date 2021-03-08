import sys
import time
import uuid

import ujson

from ml_serving import Config # type: ignore
from ml_serving.client import ServingClient

config = Config()
client = ServingClient(config)

data = "Hello world"
key = client.run_prediction(data)
pred = client.wait_answer(key)
config.logger.info(pred)

client.close()
