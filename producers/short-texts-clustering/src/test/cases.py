import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import Dict, List, Union
from server.handlers import ClientInput, ClusteringAnswer

TEST_CASE_POS: ClientInput = {
    "a": "pussy",
    "b": "pussy",
    "c": "pussy",
    "d": "pussy",
    "e": "money",
    "f": "money",
    "g": "money",
    "h": "money",
    "i": "weed",
    "j": "weed",
    "k": "weed",
    "l": "weed",
    "m": "sports"
}

ANSWER_POS: ClusteringAnswer = {
    "titles": {"-1": "none", "1": "pussy", "2": "money", "3": "weed"},
    "labels": {"-1": ["m"], "1": ["a", "b", "c", "d"], "2": ["e", "f", "g", "h"], "3": ["i", "j", "k", "l"]}
}


TEST_CASE_NEG: ClientInput = {
    "a": "\]{asdas[90-",
    "b": "хтонь",
    "c": "хтонь",
    "d": "äöpüasd",
    "e": "plainText"
}

ANSWER_NEG: ClusteringAnswer = {
    "titles": {"-1": "none"},
    "labels": {"-1": ["a", "b", "c", "d", "e"]}
}
