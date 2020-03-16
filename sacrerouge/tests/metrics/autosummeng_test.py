import json
import unittest
from typing import List

from sacrerouge.common.testing import FIXTURES_ROOT
from sacrerouge.metrics import AutoSummENG

_duc2004_file_path = 'datasets/duc-tac/duc2004/task2.jsonl'
_centroid_file_path = f'{FIXTURES_ROOT}/data/hong2014/centroid.jsonl'


class TestAutoSummENG(unittest.TestCase):
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

    def test_autosummeng(self):
        """Verify AutoSummENG runs"""
        autosummeng = AutoSummENG()
        duc2004 = self._load_multiple_summaries(_duc2004_file_path)
        centroid = self._load_summaries(_centroid_file_path)

        autosummeng.score_all(centroid, duc2004)
