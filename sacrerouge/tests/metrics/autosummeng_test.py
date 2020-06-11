import unittest

from sacrerouge.common.testing import FIXTURES_ROOT, load_references, load_summaries
from sacrerouge.metrics import AutoSummENG

_duc2004_file_path = 'datasets/duc-tac/duc2004/v1.0/task2.jsonl'
_centroid_file_path = f'{FIXTURES_ROOT}/data/hong2014/centroid.jsonl'


class TestAutoSummENG(unittest.TestCase):
    def test_autosummeng(self):
        """Verify AutoSummENG runs"""
        autosummeng = AutoSummENG()
        duc2004 = load_references(_duc2004_file_path)
        centroid = load_summaries(_centroid_file_path)

        scores = autosummeng.score_all(centroid, duc2004)
        assert scores[:5] == [
            {'AutoSummENG': 0.165069, 'MeMoG': 0.167011, 'NPowER': 0.196182},
            {'AutoSummENG': 0.107501, 'MeMoG': 0.111192, 'NPowER': 0.14895},
            {'AutoSummENG': 0.153594, 'MeMoG': 0.146739, 'NPowER': 0.184018},
            {'AutoSummENG': 0.135788, 'MeMoG': 0.100508, 'NPowER': 0.160705},
            {'AutoSummENG': 0.153668, 'MeMoG': 0.18651, 'NPowER': 0.19601}
        ]

    def test_score_multi_all_order(self):
        """Tests to ensure the scoring returns the same results, no matter the order."""
        autosummeng = AutoSummENG()
        duc2004 = load_references(_duc2004_file_path)
        centroid1 = load_summaries(_centroid_file_path)
        centroid2 = list(reversed(centroid1))  # Just create a second fake dataset

        summaries_list = list(zip(*[centroid1, centroid2]))
        metrics_lists1 = autosummeng.score_multi_all(summaries_list, duc2004)
        metrics_lists1 = list(zip(*metrics_lists1))

        summaries_list = list(zip(*[centroid2, centroid1]))
        metrics_lists2 = autosummeng.score_multi_all(summaries_list, duc2004)
        metrics_lists2 = list(zip(*metrics_lists2))

        metrics_lists2 = list(reversed(metrics_lists2))
        assert metrics_lists1 == metrics_lists2
