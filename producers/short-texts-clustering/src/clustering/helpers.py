import re
from typing import Dict

import numpy as np
import fasttext # type: ignore

from scipy.linalg import norm as l2norm # type: ignore

class FasttextPredictor:

    def __init__(self, path: str):
        # NOTE: during experiments i've used this model: cc.en.300.bin
        self.__model = fasttext.load_model(path)
        self.__regex = re.compile("\W+")
    
    def get_features(self, text: str) -> Dict[str, np.ndarray]:
        splitted = set(self.__regex.split(text))
        mean_vec, min_vec, max_vec = np.zeros(300), np.zeros(300), np.zeros(300)

        max_vec_norm = -np.inf
        min_vec_norm = np.inf
        i = 0
        for w in splitted:
            vec = self.__model.get_word_vector(w)
            norm = l2norm(vec) 
            if norm < min_vec_norm:
                min_vec = vec 
            if norm > max_vec_norm:
                max_vec = vec 
            if norm > 0:
                mean_vec += vec / norm
                i += 1
        mean_vec /= i
        return {
            "max": max_vec,
            "min": min_vec,
            "mean": mean_vec
	    }
    
    def get_lang(self, s, prob: float = 0.6, filter_lang: str = "en") -> str:
        lang, conf = self.__model.predict(s)
        lang, conf = lang[0].split("__")[-1], conf[0]
        if lang == filter_lang and conf >= prob:
            return lang
        return ""

class NaiveLangDetector:

    def __init__(self):
        self.__latin_letters = set(u"qwertyuiopasdfghjklzxcvbnm")
        self.__digits = set(u"1234567890")

    def get_lang(self, text: str) -> str:
        letters = list(text.lower().strip())
        d = {"latin":0, "digits":0, "other":0}
        for letter in letters:
            if letter in self.__latin_letters:
                d["latin"] += 1
            elif letter in self.__digits: 
                d["digits"] += 1
            else: 
                d["other"] += 1
        if d["digits"] < len(letters):
            d["digits"] = 0
        else:
            return "latin"
        return sorted(d.items(), key=lambda v: v[1], reverse=True)[0][0]
