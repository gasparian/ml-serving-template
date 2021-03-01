import sys
import time
import uuid

import ujson

from ml_serving_common import Config # type: ignore
from ml_serving_common.client import ServingClient

config = Config()
client = ServingClient(config)

data = "Hello world"
pred = client.run_prediction(data)
config.logger.info(pred)

client.close()
