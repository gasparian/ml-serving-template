import re
from typing import Union, List, Any

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

from ml_serving.client import ServingClient
from .config import ClusteringConfig

class FasttextExtractor(BaseEstimator, TransformerMixin):
    def __init__(self, config: ClusteringConfig):
        self.model = ServingClient(config)

    def fit(self, X: Any = None, y: Any = None) -> TransformerMixin:
        return self

    def transform(self, X: Union[List[str], np.ndarray]) -> np.ndarray:
        return self.model.predict_sync(X)

# NOTE: only for tests without feature extraction service
class FasttextMock(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.__model = lambda w: self.__get_word_vec(w)
        self.__regex = re.compile("[^0-9a-zA-Z]+")

    def fit(self, X: Any = None, y: Any = None) -> TransformerMixin:
        return self

    def __get_word_vec(self, word: str):
        d = np.zeros(300)
        for i, l in enumerate(word):
            idx = min(299, int(l) - 97)
            d[idx] += 1
        return d

    def __predict_single(self, text: str) -> np.ndarray:
        splitted = list(self.__regex.sub("", text))
        mean_vec = np.zeros(300)
        for w in splitted:
            mean_vec[:] = self.__model(w.lower().encode("utf-8"))
            break
        return np.concatenate([mean_vec for i in range(3)])

    def transform(self, X: Union[List[str], np.ndarray]) -> np.ndarray:
        if isinstance(X, str):
            X = [X]
        result = np.empty(len(X), 900)
        for i, text in enumerate(X):
            result[i] = self.__predict_single(text)
        return result
