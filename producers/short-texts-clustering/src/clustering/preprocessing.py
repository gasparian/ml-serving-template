import re
from typing import Optional, List

class Preprocessor:

    def __init__(self, stop_words: Optional[List[str]], placeholder: str = ""):
        if stop_words is None:
            stop_words = []
        self.__stop_words = set(stop_words)
        self.__placeholder = placeholder
        self.__regex_split = re.compile("_|\W+")
        self.__regex_sub_dates = re.compile('|'.join([
            "january", "february", "march", "april",
            "may", "june", "july", "august", "september",
            "october", "november", "december"
        ]))
        self.__regex_sub_days = re.compile('|'.join([
            "yesterday", "monday", "tuesday", "wednesday",
            "thursday", "friday", "saturday", "sunday", 
            "today", "tomorrow"
        ]))
        self.__regex_sub_year = re.compile('|'.join(list(map(lambda n: str(n), range(2010, 2099)))))
        self.__regex_sub_digit_dates = re.compile(
            "\d{2}-\d{2}-\d{4}|\d{2}:\d{2}:\d{4}|\d{2} \d{2} \d{4}|\d{2}/\d{2}/\d{4}|"+
            "\d{4}-\d{2}-\d{2}|\d{4}:\d{2}:\d{2}|\d{4} \d{2} \d{2}|\d{4}/\d{2}/\d{2}|"+
            "\d{2}-\d{2}-\d{2}|\d{2}:\d{2}:\d{2}|\d{2} \d{2} \d{2}|\d{2}/\d{2}/\d{2}"
        )
        self.__regex_sub_enums_dates = re.compile("\d{2}rd|\d{2}th")
        self.__regex_sub_digits = re.compile("\d+")

    def run(self, text: str, replace_digits=False, replace_dates=False) -> str:
        text = text.lower().strip()
        text = text.replace('&', ' and ')
      
        # replace months and days with a month/day word
        if replace_dates:
            text = " ".join(self.__regex_split.split(text))
            text = self.__regex_sub_dates.sub(' month ', text)
            text = self.__regex_sub_days.sub(' day ', text)
    
        # replace digits and dates with `date` word
        if replace_digits:
            text = self.__regex_sub_year.sub(' date ', text)
            text = self.__regex_sub_digit_dates.sub(" date ", text)
            text = self.__regex_sub_enums_dates.sub(" date ", text)
            text = self.__regex_sub_digits.sub("digit", text)
    
        filtered_tokens: List[str] = [
            w for w in text.split() 
            if w not in self.__stop_words
            and len(w) > 2
        ]
        text = " ".join(filtered_tokens).strip()
        if len(text) == 0:
            text = self.__placeholder
        return text
