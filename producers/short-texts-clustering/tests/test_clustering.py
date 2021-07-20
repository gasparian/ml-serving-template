from typing import Dict, List
import unittest
import requests
import ujson

import cases

def labels_check(inp: Dict[str, List[str]], gt: Dict[str, List[str]]) -> bool: 
    for v_gt in gt.values():
        found = False
        for v_inp in inp.values():
            intersect_len = len(set(v_gt).intersection(set(v_inp)))
            if intersect_len == len(v_gt) == len(v_inp):
                found = True
                break
        if not found:
            return False
    return True

class TestClustering(unittest.TestCase):
    _endpoint = "http://localhost:5000/api/v1/predict"

    def check(self, test_case: Dict[str, str], answer: Dict[str, List[str]]) -> None:
        serilized_test_case = ujson.dumps(test_case)
        response = requests.post(self._endpoint, data=serilized_test_case)
        resp_content = ujson.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(labels_check(resp_content, answer))

    def test_positive(self):
        self.check(cases.TEST_CASE_POS, cases.ANSWER_POS)

    def test_negative(self):
        self.check(cases.TEST_CASE_NEG, cases.ANSWER_NEG)

if __name__ == '__main__':
    unittest.main(verbosity=2)
