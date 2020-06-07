import pytest
import unittest

from sacrerouge.common.testing import FIXTURES_ROOT, load_references, load_summaries
from sacrerouge.metrics import BertScore

try:
    import bert_score
except ImportError:
    bertscore_installed = False
else:
    bertscore_installed = True

_duc2004_file_path = 'datasets/duc-tac/duc2004/task2.jsonl'
_centroid_file_path = f'{FIXTURES_ROOT}/data/hong2014/centroid.jsonl'


@unittest.skipIf(not bertscore_installed, '"bert_score" not installed')
class TestBertScore(unittest.TestCase):
    def test_bertscore(self):
        """Verify BertScore runs"""
        metric = BertScore()
        duc2004 = load_references(_duc2004_file_path)
        centroid = load_summaries(_centroid_file_path)

        scores = metric.score_all(centroid, duc2004)
        assert scores[0]['bertscore'] == pytest.approx({"precision": 0.8586893677711487, "recall": 0.8661526441574097, "f1": 0.8606264591217041}, abs=1e-4)
        assert scores[1]['bertscore'] == pytest.approx({"precision": 0.8410817384719849, "recall": 0.858047366142273, "f1": 0.8494798541069031}, abs=1e-4)
        assert scores[2]['bertscore'] == pytest.approx({"precision": 0.8831360340118408, "recall": 0.8903989791870117, "f1": 0.8867526054382324}, abs=1e-4)
        assert scores[3]['bertscore'] == pytest.approx({"precision": 0.8575657606124878, "recall": 0.8741016387939453, "f1": 0.8657547235488892}, abs=1e-4)
        assert scores[4]['bertscore'] == pytest.approx({"precision": 0.8504685759544373, "recall": 0.8628666996955872, "f1": 0.8566227555274963}, abs=1e-4)

    def test_bertscore_idf(self):
        """Verify BertScore with IDF runs"""
        metric = BertScore(idf=True)
        duc2004 = load_references(_duc2004_file_path)
        centroid = load_summaries(_centroid_file_path)

        scores = metric.score_all(centroid, duc2004)
        assert scores[0]['bertscore'] == pytest.approx({"precision": 0.8483390808105469, "recall": 0.8572883605957031, "f1": 0.8497514128684998}, abs=1e-4)
        assert scores[1]['bertscore'] == pytest.approx({"precision": 0.8177914023399353, "recall": 0.8404658436775208, "f1": 0.8284647464752197}, abs=1e-4)
        assert scores[2]['bertscore'] == pytest.approx({"precision": 0.8707811236381531, "recall": 0.8795353770256042, "f1": 0.8751363158226013}, abs=1e-4)
        assert scores[3]['bertscore'] == pytest.approx({"precision": 0.832008421421051, "recall": 0.8596619963645935, "f1": 0.8450315594673157}, abs=1e-4)
        assert scores[4]['bertscore'] == pytest.approx({"precision": 0.8320634961128235, "recall": 0.8453822731971741, "f1": 0.838670015335083}, abs=1e-4)

    def test_score_multi_all_order(self):
        """Tests to ensure the scoring returns the same results, no matter the order."""
        metric = BertScore()
        duc2004 = load_references(_duc2004_file_path)
        centroid1 = load_summaries(_centroid_file_path)
        centroid2 = list(reversed(centroid1))  # Just create a second fake dataset

        summaries_list = list(zip(*[centroid1, centroid2]))
        metrics_lists1 = metric.score_multi_all(summaries_list, duc2004)
        metrics_lists1 = list(zip(*metrics_lists1))

        summaries_list = list(zip(*[centroid2, centroid1]))
        metrics_lists2 = metric.score_multi_all(summaries_list, duc2004)
        metrics_lists2 = list(zip(*metrics_lists2))

        metrics_lists2 = list(reversed(metrics_lists2))
        assert metrics_lists1 == metrics_lists2
