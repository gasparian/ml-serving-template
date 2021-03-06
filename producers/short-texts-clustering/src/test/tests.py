import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import ujson
import unittest

import requests

import cases # type: ignore
from server.handlers import ClientInput, Labels, ClusteringAnswer

def labels_check(inp: Labels, gt: Labels) -> bool: 
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
    endpoints = [
        "http://localhost:5000/get-clusters/fasttext",
        "http://localhost:5000/get-clusters/tfidf"
    ]

    def check(self, test_case: ClientInput, answer: ClusteringAnswer) -> None:
        serilized_test_case = ujson.dumps(test_case)
        for endpoint in self.endpoints:
            response = requests.post(endpoint, data=serilized_test_case)
            resp_content = ujson.loads(response.content)

            print(endpoint)
            print(resp_content)
            print(answer)

            self.assertEqual(response.status_code, 200)
            titles_check = set(resp_content["titles"].values()).intersection(set(answer["titles"].values()))
            self.assertTrue(len(titles_check) == len(answer["titles"].values()))
            self.assertTrue(labels_check(resp_content["labels"], answer["labels"]))

    def test_positive(self):
        self.check(cases.TEST_CASE_POS, cases.ANSWER_POS)

    def test_negative(self):
        self.check(cases.TEST_CASE_NEG, cases.ANSWER_NEG)

if __name__ == '__main__':
    tmp = unittest.main(exit=False, verbosity=0)
    print(int(tmp.result.wasSuccessful()))
