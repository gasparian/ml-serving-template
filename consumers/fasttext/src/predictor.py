import re
from typing import Union, List, Dict, Any

import ujson
import fasttext # type: ignore
import numpy as np
from ml_serving.inference import PredictorBase # type: ignore

Prediction = Dict[str, np.ndarray]

class Predictor(PredictorBase):
    def __init__(self, path: str):
        # NOTE: model: cc.en.300.bin has been used during the experiment
        self.__model = fasttext.load_model(path)
        self.__regex = re.compile("\W+")

    def __predict_single(self, text: str):
        splitted = set(self.__regex.split(text))
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
        return {
            "max": max_vec.tolist(),
            "min": min_vec.tolist(),
            "mean": mean_vec.tolist()
	    }

    def predict(self, data: Union[str, List[str], np.ndarray]):
        if isinstance(data, str):
            data = [data]
        result: List[Any] = []
        for text in data:
            result.append(self.__predict_single(text))
        return result

# NOTE: only for tests without feature extraction service
class PredictorMock(PredictorBase):
    """
    Needed for tests only.
    It gets the first word, computes the hash
    and populates the whole vector with it
    """
    def __init__(self):
        self.__model = lambda w: self.__get_word_vec(w)
        self.__regex = re.compile("[^0-9a-zA-Z]+")

    def __get_word_vec(self, word: str):
        d = np.zeros(300)
        for i, l in enumerate(word):
            idx = min(299, int(l) - 97)
            d[idx] += 1
        return d

    def __predict_single(self, text: str):
        splitted = list(self.__regex.sub("", text))
        mean_vec = np.zeros(300)
        for w in splitted:
            mean_vec[:] = self.__model(w.lower().encode("utf-8"))
            break
        min_vec = max_vec = mean_vec
        return {
            "max": max_vec,
            "min": min_vec,
            "mean": mean_vec
        }

    def predict(self, data: Union[str, List[str], np.ndarray]):
        if isinstance(data, str):
            data = [data]
        result: List[Any] = []
        for text in data:
            result.append(self.__predict_single(text))
        return result
