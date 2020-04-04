import unittest

from sacrerouge.common.testing import FIXTURES_ROOT, load_references, load_summaries
from sacrerouge.metrics import AutoSummENG

_duc2004_file_path = 'datasets/duc-tac/duc2004/task2.jsonl'
_centroid_file_path = f'{FIXTURES_ROOT}/data/hong2014/centroid.jsonl'


class TestAutoSummENG(unittest.TestCase):
    def test_autosummeng(self):
        """Verify AutoSummENG runs"""
        autosummeng = AutoSummENG()
        duc2004 = load_references(_duc2004_file_path)
        centroid = load_summaries(_centroid_file_path)

        autosummeng.score_all(centroid, duc2004)
