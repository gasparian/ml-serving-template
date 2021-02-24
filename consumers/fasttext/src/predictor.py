import os
os.sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))) # type: ignore

import re
from typing import Dict, Any

import ujson
import fasttext # type: ignore
import numpy as np
from common.inference import PredictorBase # type: ignore

Prediction = Dict[str, np.ndarray]

class Predictor(PredictorBase):
    def __init__(self, path: str):
        # NOTE: model: cc.en.300.bin has been used during the experiment
        self.__model = fasttext.load_model(path)
        self.__regex = re.compile("\W+")

    def predict(self, data: bytes) -> str:
        splitted = set(self.__regex.split(data.decode()))
        mean_vec, min_vec, max_vec = np.zeros(300), np.zeros(300), np.zeros(300)

        max_vec_norm = -np.inf
        min_vec_norm = np.inf
        i = 0
        for w in splitted:
            vec = self.__model.get_word_vector(w)
            norm = np.linalg.norm(vec) 
            if norm < min_vec_norm:
                min_vec = vec 
            if norm > max_vec_norm:
                max_vec = vec 
            if norm > 0:
                mean_vec += vec / norm
                i += 1
        mean_vec /= i
        return ujson.dumps({
            "max": max_vec.tolist(),
            "min": min_vec.tolist(),
            "mean": mean_vec.tolist()
	    })

class PredictorMock(PredictorBase):
    def __init__(self, path: str):
        pass

    def predict(self, data: bytes) -> str:
        return ujson.dumps({
            "max": np.full(10, 1).tolist(),
            "min": np.full(10, 0).tolist(),
            "mean": np.full(10, 0.5).tolist()
        })
