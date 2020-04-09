import os
import pytest
import unittest

from sacrerouge.common.testing import FIXTURES_ROOT, load_references, load_summaries
from sacrerouge.metrics import MoverScore
from sacrerouge.metrics.moverscore import MOVERSCORE_EXISTS

_duc2004_file_path = 'datasets/duc-tac/duc2004/task2.jsonl'
_centroid_file_path = f'{FIXTURES_ROOT}/data/hong2014/centroid.jsonl'


@pytest.mark.skipif(not MOVERSCORE_EXISTS, reason='MoverScore not setup')
@pytest.mark.skipif(not os.path.exists(_duc2004_file_path), reason='DUC 2004 data does not exist')
@pytest.mark.skipif(not os.path.exists(_centroid_file_path), reason='Hong 2014 data does not exist')
class TestMoverScore(unittest.TestCase):
    def test_mover_score_runs(self):
        # These numbers were not checked to be correct, but will detect if anything
        # changes in the code
        duc2004 = load_references(_duc2004_file_path)
        centroid = load_summaries(_centroid_file_path)

        moverscore = MoverScore()
        _, metrics_list = moverscore.evaluate(centroid, duc2004)
        assert metrics_list[0]['MoverScore'] == pytest.approx(0.24826391722135857, abs=1e-4)
        assert metrics_list[1]['MoverScore'] == pytest.approx(0.19464766520457838, abs=1e-4)
        assert metrics_list[2]['MoverScore'] == pytest.approx(0.26644948499030685, abs=1e-4)
        assert metrics_list[3]['MoverScore'] == pytest.approx(0.21231040174382498, abs=1e-4)
        assert metrics_list[4]['MoverScore'] == pytest.approx(0.15387569485290115, abs=1e-4)

    def test_score_multi_all_order(self):
        """Tests to ensure the scoring returns the same results, no matter the order."""
        moverscore = MoverScore()
        duc2004 = load_references(_duc2004_file_path)
        centroid1 = load_summaries(_centroid_file_path)
        centroid2 = list(reversed(centroid1))  # Just create a second fake dataset

        summaries_list = list(zip(*[centroid1, centroid2]))
        metrics_lists1 = moverscore.score_multi_all(summaries_list, duc2004)
        metrics_lists1 = list(zip(*metrics_lists1))

        summaries_list = list(zip(*[centroid2, centroid1]))
        metrics_lists2 = moverscore.score_multi_all(summaries_list, duc2004)
        metrics_lists2 = list(zip(*metrics_lists2))

        metrics_lists2 = list(reversed(metrics_lists2))
        assert metrics_lists1 == metrics_lists2
