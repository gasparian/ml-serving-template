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
    _endpoint = "http://localhost:5000/api/v1/predict"

    def check(self, test_case: ClientInput, answer: ClusteringAnswer) -> None:
        serilized_test_case = ujson.dumps(test_case)
        response = requests.post(self._endpoint, data=serilized_test_case)
        resp_content = ujson.loads(response.content)

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
    unittest.main(verbosity=2)

# import os
# import sys

# import falcon
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# import logging
# import unittest

# import ujson
# from falcon import testing

# import cases # type: ignore
# from helpers import labels_check
# import api

# logging.basicConfig(
#     level=logging.DEBUG,
#     format="[%(levelname)s] [%(asctime)s] %(message)s",
#     datefmt="%d/%b/%Y %H:%M:%S",
#     stream=sys.stdout
# )

# class ClusterTest(testing.TestCase):
#     _config = api.Config(
#         min_cluster_size=3,
#         center_vectors=0,
#         cosine_thrsh=0.1,
#         max_title_len=4
#     )
#     _app = api.create(_config, logging.getLogger())
#     def setUp(self):
#         super(ClusterTest, self).setUp()
#         self.app = self._app

# class TestApi(ClusterTest):
#     def _check(self, endpoint: str, test_case: cases.ClientInput, answer: cases.ClusteringAnswer) -> None:
#         serilized_test_case = ujson.dumps(test_case)
#         response = self.simulate_post(endpoint, body=serilized_test_case)
#         resp_content = ujson.loads(response.content)
#         self.assertEqual(response.status, falcon.HTTP_200)
#         titles_check = set(resp_content["titles"].values()).intersection(set(answer["titles"].values()))
#         self.assertTrue(len(titles_check) == len(answer["titles"].values()))
#         self.assertTrue(labels_check(resp_content["labels"], answer["labels"]))

#     def test_health(self):
#         result = self.simulate_get('/')
#         self.assertEqual(result.status, falcon.HTTP_200)

#     def test_positive_fasttext(self):
#         self._check("/api/v1/predict", cases.TEST_CASE_POS, cases.ANSWER_POS)

#     def test_negative_fasttext(self):
#         self._check("/api/v1/predict", cases.TEST_CASE_NEG, cases.ANSWER_NEG)

# if __name__ == '__main__':
#     unittest.main(verbosity=2)