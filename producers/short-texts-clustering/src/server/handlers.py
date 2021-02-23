import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import Union, Dict, List, Optional, Any
import numpy as np
from clustering import ClusteringPipeline

ClientInput = Dict[str, str]
Labels = Union[Dict[str, str], Dict[str, List[str]]]
ClusteringAnswer = Dict[str, Labels]

class ClusteringPipelineHandler(ClusteringPipeline):

    def __init__(self, models_path: str, stop_words: Optional[List[str]] = None):
        super().__init__(models_path, stop_words)

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

# import sys
# import logging

# import fasttext
# import falcon
# import ujson

# logging.basicConfig(
#     level=logging.DEBUG,
#     format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
#     datefmt="%d/%b/%Y %H:%M:%S",
#     stream=sys.stdout
# )
# logger = logging.getLogger()

# class ResponseLoggerMiddleware(object):
#     def process_response(self, req, resp, resource, req_succeeded):
#         logger.info('{0} {1} {2}'.format(req.method, req.relative_uri, resp.status[:3]))

# class Status(object):
#     def on_get(self, req, resp):
#         resp.body = b"OK"
#         resp.status = falcon.HTTP_200

# class Predictor(object):
#     def on_post(self, req, resp):
#         form = req.params
#         if 'text' in form and form['text']:
#             try:
#                 output = form["text"]
#                 resp.body = ujson.dumps({"output" : output})
#                 resp.status = falcon.HTTP_200
#             except:
#                 resp.body = ujson.dumps({'Error': 'An internal server error has occurred'})
#                 resp.status = falcon.HTTP_500
#         else:
#             resp.body = ujson.dumps({'Error': 'param \'text\' is mandatory'})
#             resp.status = falcon.HTTP_400
