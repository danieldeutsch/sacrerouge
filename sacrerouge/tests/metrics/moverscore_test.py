import os
import pytest
import unittest

from sacrerouge.common.testing import FIXTURES_ROOT, load_references, load_summaries
from sacrerouge.metrics import MoverScore

_duc2004_file_path = 'datasets/duc-tac/duc2004/task2.jsonl'
_centroid_file_path = f'{FIXTURES_ROOT}/data/hong2014/centroid.jsonl'


class TestMoverScore(unittest.TestCase):
    @pytest.mark.skipif(not os.path.exists(_duc2004_file_path), reason='DUC 2004 data does not exist')
    @pytest.mark.skipif(not os.path.exists(_centroid_file_path), reason='Hong 2014 data does not exist')
    def test_mover_score_runs(self):
        duc2004 = load_references(_duc2004_file_path)
        centroid = load_summaries(_centroid_file_path)

        moverscore = MoverScore()
        _, metrics_list = moverscore.evaluate(centroid, duc2004)
        print(metrics_list[:5])
