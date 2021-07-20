import re
from typing import Union, List

import fasttext # type: ignore
import numpy as np
from ml_serving.inference import PredictorBase # type: ignore

class Predictor(PredictorBase):
    def __init__(self, path: str):
        # NOTE: model: cc.en.300.bin has been used during the experiment
        self.__model = fasttext.load_model(path)
        self.__regex = re.compile("\W+")

    def __predict_single(self, text: str) -> np.ndarray:
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
        if i > 0:
            mean_vec /= i
        return np.concatenate([mean_vec, min_vec, max_vec])

    def predict(self, data: Union[str, List[str], np.ndarray]) -> np.ndarray:
        if isinstance(data, str):
            data = [data]
        result = np.empty((len(data), 900))
        for i, text in enumerate(data):
            result[i] = self.__predict_single(text)
        return result
