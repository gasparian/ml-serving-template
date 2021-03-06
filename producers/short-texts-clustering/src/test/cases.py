import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import Dict, List, Union
from server.handlers import ClientInput, ClusteringAnswer

TEST_CASE_POS: ClientInput = {
    "a": "door",
    "b": "door",
    "c": "door",
    "d": "door",
    "e": "bull",
    "f": "bull",
    "g": "bull",
    "h": "bull",
    "i": "take",
    "j": "take",
    "k": "take",
    "l": "take",
    "m": "слово"
}

ANSWER_POS: ClusteringAnswer = {
    "titles": {"-1": "none", "1": "door", "2": "bull", "3": "take"},
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
