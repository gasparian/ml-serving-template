import re
from typing import Dict

import numpy as np

# NOTE: only for tests without feature extraction service
class FasttextPredictorMock(object):
    """
    Needed for tests only.
    It gets the first word, computes the hash
    and populates the whole vector with it
    """
    def __init__(self):
        self.__model = lambda w: self.__get_word_vec(w)
        self.__regex = re.compile("\W+")

    def __get_word_vec(self, word):
        d = np.zeros(300)
        for i, l in enumerate(word):
            idx = min(299, int(l) - 97)
            d[idx] += 1
        return d

    def get_features(self, text: str):
        splitted = list(self.__regex.split(text))
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
