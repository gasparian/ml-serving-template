import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import unittest

import requests

import cases # type: ignore
from server.handlers import ClientInput, Labels, ClusteringAnswer

def labels_check(inp: Labels, gt: Labels) -> bool: 
    for v_gt in gt.values():
        found = False
        for v_inp in inp.values():
            intersect_len = len(set(v_gt).intersection(set(v_inp)))
            if intersect_len == len(v_gt):
                found = True
                break
        if not found:
            return False
    return True

class TestClustering(unittest.TestCase):
    endpoints = map(lambda route: globals()["endpoint"] + "/get-clusters/" + route, ["fasttext", "tfidf"])

    def check(self, test_case: ClientInput, answer: ClusteringAnswer) -> None:
        serilized_test_case = json.dumps(test_case)
        for endpoint in self.endpoints:
            response = requests.post(endpoint, data=serilized_test_case)
            self.assertEqual(response.status_code, 200)
            resp_content = json.loads(response.content)
            self.assertEqual(resp_content["status"], "success")
            titles_check = set(resp_content["result"]["titles"].values()).intersection(set(answer["titles"].values()))
            self.assertTrue(len(titles_check) == len(answer["titles"].values()))
            self.assertTrue(labels_check(resp_content["result"]["labels"], answer["labels"]))

    def test_positive(self):
        self.check(cases.TEST_CASE_POS, cases.ANSWER_POS)

    def test_negative(self):
        self.check(cases.TEST_CASE_NEG, cases.ANSWER_NEG)

if __name__ == '__main__':
    endpoint = "http://localhost:5000"
    tmp = unittest.main(exit=False, verbosity=0)
    print(int(tmp.result.wasSuccessful()))
