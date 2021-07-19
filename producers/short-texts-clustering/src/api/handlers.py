import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import traceback
from typing import Dict, List

import numpy as np
import falcon
import ujson
from sklearn.pipeline import Pipeline

from clustering import Clustering, FasttextExtractor, Preprocessor

class Status(object):
    def on_get(self, req, resp):
        resp.body = b"OK"
        resp.status = falcon.HTTP_200

class ClusteringPipelineHandler:
    def __init__(self, prep: Preprocessor, extractor: FasttextExtractor, cluster: Clustering):
        self.pipe = Pipeline([
            ("prep", prep),
            ("extractor", extractor),
            ("cluster", cluster)
        ])

    def _get_clusters(self, inp: Dict[str, str]) -> Dict[str, List[str]]:
        texts: List[str] = [w for w in inp.values()]
        labels = self.pipe.fit_predict(texts)
        labels_buckets: Dict[str, List[str]] = dict()
        for key, c in zip(list(inp.keys()), labels):
            cc = str(c)
            if cc not in labels_buckets:
                labels_buckets[cc] = []
            labels_buckets[cc].append(key)
        return labels_buckets

    def on_post(self, req, resp) -> None:
        if req.content_length:
            try:
                inp = ujson.loads(req.stream.read())
                answer = self._get_clusters(inp)
                resp.body = ujson.dumps(answer)
                resp.status = falcon.HTTP_200
            except Exception as e:
                resp.body = ujson.dumps({'Error': traceback.format_exc()})
                resp.status = falcon.HTTP_500
        else:
            resp.body = ujson.dumps({'Error': 'data payload is mandatory'})
            resp.status = falcon.HTTP_400
