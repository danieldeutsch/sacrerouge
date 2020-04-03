import json
import os
import pytest
import unittest
from typing import List

from sacrerouge.common.testing import FIXTURES_ROOT
from sacrerouge.metrics import BEwTE

_duc2004_file_path = 'datasets/duc-tac/duc2004/task2.jsonl'
_centroid_file_path = f'{FIXTURES_ROOT}/data/hong2014/centroid.jsonl'


class TestBEwTE(unittest.TestCase):
    def _load_summaries(self, file_path: str) -> List[List[str]]:
        summaries = []
        with open(file_path, 'r') as f:
            for line in f:
                data = json.loads(line)
                summaries.append(data['summary'])
        return summaries

    def _load_multiple_summaries(self, file_path: str) -> List[List[List[str]]]:
        summaries = []
        with open(file_path, 'r') as f:
            for line in f:
                data = json.loads(line)
                summaries.append(data['summaries'])
        return summaries

    @pytest.mark.skipif(not os.path.exists(_duc2004_file_path), reason='DUC 2004 data does not exist')
    @pytest.mark.skipif(not os.path.exists(_centroid_file_path), reason='Hong 2014 data does not exist')
    def test_bewte_runs(self):
        duc2004 = self._load_multiple_summaries(_duc2004_file_path)
        centroid = self._load_summaries(_centroid_file_path)

        bewte = BEwTE()
        _, metrics_list = bewte.evaluate(centroid, duc2004)
        metrics_list[5]['BEwTE']['precision'] == pytest.approx(54.54545454, abs=1e-5)
        metrics_list[5]['BEwTE']['recall'] == pytest.approx(16.50488585, abs=1e-5)
        metrics_list[5]['BEwTE']['f1'] == pytest.approx(25.32239681, abs=1e-5)
