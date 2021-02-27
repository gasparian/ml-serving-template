import os
import json
import logging
from typing import Tuple

from flask import Flask, request 

from nltk.corpus import stopwords # type: ignore

from server.decorators import crossdomain, predict_wrapper # type: ignore
from server.handlers import ClusteringPipelineHandler, ClusteringAnswer # type: ignore

app = Flask(__name__)
logger = logging.getLogger('gunicorn.error')  
app.logger.handlers = logger.handlers
app.logger.setLevel(logger.level)

stops_en = stopwords.words('english')
clusterizer = ClusteringPipelineHandler(os.environ["FASTTEXT_PATH"], stops_en)

#######################################################

app.logger.info("Server started!")

@app.route('/get-clusters/fasttext', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
@predict_wrapper(logger=app.logger)
def get_clusters_fasttext() -> ClusteringAnswer:
    inp = json.loads(request.data)
    result = clusterizer.get_clusters_handler(inp, mode="fasttext")
    return result
    
@app.route('/get-clusters/tfidf', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
@predict_wrapper(logger=app.logger)
def get_clusters_tfidf() -> ClusteringAnswer:
    inp = json.loads(request.data)
    result = clusterizer.get_clusters_handler(inp, mode="tfidf")
    return result

@app.route('/', methods=['GET'])
@crossdomain(origin='*')
def healthcheck() -> str:
    return "OK"

# import falcon
# import bjoern
# from server.handlers import *
# from server.middleware improt *

# app = falcon.API(middleware=[ResponseLoggerMiddleware()])
# app.req_options.auto_parse_form_urlencoded = True

# app.add_route('/', Status())
# app.add_route('/predict', Predictor())

# print('Listening on http://localhost:5000/')
# bjoern.run(app, "0.0.0.0", 5000, reuse_port=True)