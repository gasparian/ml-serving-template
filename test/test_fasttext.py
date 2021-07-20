import sys
import time
import uuid

from ml_serving import Config # type: ignore
from ml_serving.client import ServingClient # TODO: test both sync and async clients

config = Config()
client = ServingClient(config)
data = "Hello world"

pred = client.predict_sync(data)
config.logger.info(f"Sync client: {pred}")

# key = client.predict_async(data)
# time.sleep(1)
# pred = client.get_result(key)
# config.logger.info(f"Async client: {pred}")

client.close()
