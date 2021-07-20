from typing import Dict, List
import unittest
import requests
import ujson

import cases

class TestClustering(unittest.TestCase):
    _endpoint = "http://localhost:5000/api/v1/predict"

    def check(self, test_case: Dict[str, str], answer: Dict[str, List[str]]) -> None:
        serilized_test_case = ujson.dumps(test_case)
        response = requests.post(self._endpoint, data=serilized_test_case)
        resp_content = ujson.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(resp_content, answer)

    def test_positive(self):
        for case in cases.TEST_CASES_POS:
            self.check(case, cases.ANSWER_POS)

    def test_negative(self):
        self.check(cases.TEST_CASE_NEG, cases.ANSWER_NEG)

if __name__ == '__main__':
    unittest.main(verbosity=2)
