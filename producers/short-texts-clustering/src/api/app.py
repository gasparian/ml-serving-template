import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import logging

import falcon
from .handlers import ClusteringPipelineHandler, Status
from .middleware import ResponseLogger
from clustering import ClusteringConfig

def create(config: ClusteringConfig, logger: logging.Logger) -> falcon.API:
    app = falcon.API(middleware=[ResponseLogger(logger)])
    app.req_options.auto_parse_form_urlencoded = True
    app.add_route('/', Status())
    app.add_route('/api/v1/predict', ClusteringPipelineHandler(config))
    return app
