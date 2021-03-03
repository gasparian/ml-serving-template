import os
import sys
import logging
from typing import Tuple

import falcon
import bjoern
from server.handlers import ClusteringPipelineHandler, Status
from server.middleware import ResponseLoggerMiddleware
from clustering import ClusteringConfig

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)s] [%(asctime)s] %(message)s",
    datefmt="%d/%b/%Y %H:%M:%S",
    stream=sys.stdout
)
logger = logging.getLogger()
config = ClusteringConfig()

app = falcon.API(middleware=[ResponseLoggerMiddleware(logger)])
app.req_options.auto_parse_form_urlencoded = True

app.add_route('/', Status())
# NOTE: mode can be: `fasttext` or `tfidf`
app.add_route('/get-clusters/{mode}', ClusteringPipelineHandler(config))

logger.info("Listening on http://localhost:5000/")
bjoern.run(app, "0.0.0.0", 5000, reuse_port=True)
