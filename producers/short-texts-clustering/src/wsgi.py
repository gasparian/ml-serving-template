import sys
import logging

import bjoern
import api
from clustering import ClusteringConfig

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)s] [%(asctime)s] %(message)s",
    datefmt="%d/%b/%Y %H:%M:%S",
    stream=sys.stdout
)
logger = logging.getLogger()
config = ClusteringConfig()

app = api.App(config, logger).create()

logger.info("Listening on http://localhost:5000/")
bjoern.run(app, "0.0.0.0", 5000, reuse_port=True)
