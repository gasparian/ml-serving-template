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
