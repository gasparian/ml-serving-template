from typing import List, Any, Union

import numpy as np
from sklearn.base import BaseEstimator, ClusterMixin, TransformerMixin
from nltk.corpus import stopwords # type: ignore

class Preprocessor(BaseEstimator, TransformerMixin):
    def __init__(self, stop_words: List[str] = [""]):
        self.stop_words = list(set(stopwords.words('english') + stop_words))

    def fit(self, X: Any = None, y: Any = None) -> TransformerMixin:
        return self

    def _transform_text(self, text: str) -> str:
        text = text.lower().strip()
        text = text.replace('&', ' and ')
      
        filtered_tokens: List[str] = [
            w for w in text.split()
            if w not in self.stop_words and len(w) > 2
        ]
        text = " ".join(filtered_tokens).strip()
        if text is None:
            text = ""
        return text
        
    def transform(self, X: Union[List[str], np.ndarray]) -> np.ndarray:
        output = np.empty(len(X), dtype=object)
        for i, text in enumerate(X):
            output[i] = self._transform_text(text)
        return output