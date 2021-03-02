import abc
import os
from typing import Union, Callable, List

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer # type: ignore

from .models import FasttextPredictorMock as FasttextPredictor
# from .models import FasttextPredictor

class TextFeaturesExtractor(abc.ABC):
    def __init__(self, preprocessor: Callable[[str], str]):
        self.__preprocessor = preprocessor

    def __preprocess_text(self, inp: str) -> str:
        assert(isinstance(inp, str))
        return self.__preprocessor(inp)

    def preprocess_texts(self, inp: Union[List, np.ndarray]) -> np.ndarray:
        assert(isinstance(inp, list) or isinstance(inp, np.ndarray))
        return np.array(list(map(lambda text: self.__preprocess_text(text), inp)), dtype=str)

    @abc.abstractmethod
    def get_features(self, inp: Union[List[str], np.ndarray]) -> np.ndarray:
        pass
    
class TfidfExtractor(TextFeaturesExtractor):
    def __init__(self, preprocessor: Callable[[str], str]):
        super().__init__(preprocessor)
        self.model = TfidfVectorizer( 
            strip_accents="unicode", 
            lowercase=False, 
            preprocessor=None, 
            tokenizer=None, 
            analyzer='char', # char_wb/char works pretty good
            token_pattern='\w+', 
            ngram_range=(3, 30), # 3-12 / 3-20 / 3-30
            max_df=0.9, 
            min_df=2, 
            max_features=None, 
            vocabulary=None, 
            binary=False, 
            norm='l2',
            use_idf=True, 
            smooth_idf=True, 
            sublinear_tf=False
        )
    
    def get_features(self, inp: Union[List[str], np.ndarray]) -> np.ndarray:
        return self.model.fit_transform(inp).toarray()

# TODO: rewrite method to get the features from other service
class FasttextExtractor(TextFeaturesExtractor):
    def __init__(self, preprocessor: Callable[[str], str], center_data: bool = False):
        super().__init__(preprocessor)
        self.model = FasttextPredictor()
        self.__center_data = center_data 

    def get_features(self, inp: Union[List[str], np.ndarray]) -> np.ndarray:
        vecs = np.empty((len(inp), 900))
        for i, text in enumerate(inp):
            vecs[i] = np.concatenate(list(self.model.get_features(text).values()))
        if self.__center_data:
            return vecs - vecs.mean(axis=0)
        else:
            return vecs
