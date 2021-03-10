import sys
import time
import uuid

import ujson

from ml_serving import Config # type: ignore
from ml_serving.client import ServingClient # TODO: test both sync and async clients

config = Config()
client = ServingClient(config)
data = "Hello world"

pred = client.predict_sync(data)

# key = client.predict_async(data)
# pred = client.get_result(key)

config.logger.info(pred)
client.close()
