import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import traceback
from typing import Union, Dict, List, Optional, Any

from nltk.corpus import stopwords # type: ignore
import numpy as np
import falcon
import ujson

from clustering import ClusteringPipeline

class Status(object):
    def on_get(self, req, resp):
        resp.body = b"OK"
        resp.status = falcon.HTTP_200

ClientInput = Dict[str, str]
Labels = Union[Dict[str, str], Dict[str, List[str]]]
ClusteringAnswer = Dict[str, Labels]

class ClusteringPipelineHandler(ClusteringPipeline):
    def __init__(self):
        stops_en = stopwords.words('english')
        super().__init__(stops_en)

    def get_clusters_handler(self, inp: ClientInput, mode: str = "tfidf") -> ClusteringAnswer:
        texts: List[str] = [w for w in inp.values()]
        titles, labels = self.get_clusters(texts, features_type=mode)
        labels_buckets: Dict[str, List[str]] = dict()
        for key, c in zip(list(inp.keys()), labels):
            cc = str(c)
            if cc not in labels_buckets:
                labels_buckets[cc] = []
            labels_buckets[cc].append(key)
        result: ClusteringAnswer = {
            "titles": dict((str(k), v) for k, v in titles.items()), 
            "labels": labels_buckets
        }
        return result

    def on_post(self, req, resp, mode: str) -> None:
        if req.content_length:
            try:
                inp = ujson.loads(req.stream.read())
                answer = self.get_clusters_handler(inp, mode)
                resp.body = ujson.dumps(answer)
                resp.status = falcon.HTTP_200
            except Exception as e:
                resp.body = ujson.dumps({'Error': traceback.format_exc()})
                resp.status = falcon.HTTP_500
        else:
            resp.body = ujson.dumps({'Error': 'data payload is mandatory'})
            resp.status = falcon.HTTP_400
