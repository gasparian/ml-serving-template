import re
from typing import Dict

import numpy as np
import fasttext # type: ignore

from scipy.linalg import norm as l2norm # type: ignore

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
