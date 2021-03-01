import time

import numpy as np
import falcon

def timer() -> float:
    return int(round(time.perf_counter() * 1000))

class ResponseLoggerMiddleware(object):
    def __init__(self, logger):
        self.logger = logger

    def process_request(self, req: falcon.Request, resp: falcon.Response):
        req.context["X-start-time"] = timer()

    def process_response(self, req: falcon.Request, resp: falcon.Response, resource, req_succeeded: bool):
        dt = timer() - req.context.pop("X-start-time")
        self.logger.info('{0} {1} {2} Timeout: {3} ms'.format(req.method, req.relative_uri, resp.status[:3], dt))
