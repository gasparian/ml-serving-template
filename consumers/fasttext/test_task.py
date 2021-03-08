import sys
import time
import uuid

import ujson

from ml_serving import Config # type: ignore
from ml_serving.client import ServingRpcClient

config = Config()
client = ServingRpcClient(config)

data = "Hello world"
client.run_prediction(data)
pred = client.get_answer()
config.logger.info(pred)

client.close()
