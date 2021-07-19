import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import logging

import falcon
from .handlers import ClusteringPipelineHandler, Status
from .middleware import ResponseLogger
from clustering import ClusteringConfig, Preprocessor, FasttextExtractor, FasttextMock, Clustering

class App:
    def __init__(self, config: ClusteringConfig, logger: logging.Logger) -> None:
        self.config = config
        self.app = falcon.API(middleware=[ResponseLogger(logger)])
        self.app.req_options.auto_parse_form_urlencoded = True
        self.app.add_route('/', Status())

    def create(self) -> falcon.API:
        self.app.add_route(
            '/api/v1/predict', 
            ClusteringPipelineHandler(
                Preprocessor(),
                FasttextExtractor(self.config),
                Clustering(self.config.min_cluster_size, self.config.cosine_thrsh)
            )
        )
        return self.app

    def create_mock(self) -> falcon.API:
        self.app.add_route(
            '/api/v1/predict', 
            ClusteringPipelineHandler(
                Preprocessor(),
                FasttextMock(),
                Clustering(self.config.min_cluster_size, self.config.cosine_thrsh)
            )
        )
        return self.app