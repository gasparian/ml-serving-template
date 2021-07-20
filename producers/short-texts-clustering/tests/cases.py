from typing import Dict, List

TEST_CASE_POS: Dict[str, str] = {
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

ANSWER_POS: Dict[str, List[str]] = {
    "-1": ["m"], "0": ["a", "b", "c", "d"], "1": ["e", "f", "g", "h"], "2": ["i", "j", "k", "l"]
}

TEST_CASE_NEG: Dict[str, str] = {
    "a": "\]{asdas[90-",
    "b": "хтонь",
    "c": "хтонь",
    "d": "äöpüasd",
    "e": "plainText"
}

ANSWER_NEG: Dict[str, List[str]] = {
    "-1": ["a", "b", "c", "d", "e"]
}
