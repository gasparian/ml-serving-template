import time
import json
from datetime import timedelta
from functools import update_wrapper
import traceback

import numpy as np
from flask import request, current_app, make_response, jsonify

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):

    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, str):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['Access-Control-Allow-Credentials'] = 'true'
            h['Access-Control-Allow-Headers'] = \
              "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        #f.required_methods = ['OPTIONS']
        return update_wrapper(wrapped_function, f)
    return decorator

def convert(o):
    if isinstance(o, np.int64):
        return int(o)
    raise TypeError

def predict_wrapper(logger):
    def decorator(func):
        def wrapper():
            start = time.time()
            status = "success"
            try:
                out = func()
            except Exception as e:
                status = "failed"
                out = traceback.format_exc()
                logger.error(out)
            result = jsonify(status=status, result=out)
            result.status_code = 200
            logger.info("handler: {}, status: {}, took: {} ms".format(
                func.__name__,
                status,
                round((time.time() - start)*1000, 1)
            ))
            return result
        return update_wrapper(wrapper, func)
    return decorator
