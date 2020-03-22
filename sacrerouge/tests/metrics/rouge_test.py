import json
import os
import pytest
import unittest
from typing import List

from sacrerouge.common.testing import FIXTURES_ROOT
from sacrerouge.metrics import Rouge

_duc2004_file_path = 'datasets/duc-tac/duc2004/task2.jsonl'
_centroid_file_path = f'{FIXTURES_ROOT}/data/hong2014/centroid.jsonl'
_classy04_file_path = f'{FIXTURES_ROOT}/data/hong2014/classy04.jsonl'
_classy11_file_path = f'{FIXTURES_ROOT}/data/hong2014/classy11.jsonl'
_dpp_file_path = f'{FIXTURES_ROOT}/data/hong2014/dpp.jsonl'
_freq_sum_file_path = f'{FIXTURES_ROOT}/data/hong2014/freq-sum.jsonl'
_greedy_kl_file_path = f'{FIXTURES_ROOT}/data/hong2014/greedy-kl.jsonl'
_icsi_summ_file_path = f'{FIXTURES_ROOT}/data/hong2014/icsi-summ.jsonl'
_lexrank_file_path = f'{FIXTURES_ROOT}/data/hong2014/lexrank.jsonl'
_occams_v_file_path = f'{FIXTURES_ROOT}/data/hong2014/occams-v.jsonl'
_reg_sum_file_path = f'{FIXTURES_ROOT}/data/hong2014/reg-sum.jsonl'
_submodular_file_path = f'{FIXTURES_ROOT}/data/hong2014/submodular.jsonl'
_ts_sum_file_path = f'{FIXTURES_ROOT}/data/hong2014/ts-sum.jsonl'


class TestRouge(unittest.TestCase):
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
    def test_hong2014(self):
        """
        Tests to ensure that the Rouge scores for the summaries from Hong et al. 2014
        (http://www.lrec-conf.org/proceedings/lrec2014/pdf/1093_Paper.pdf) do not
        change. The hard-coded scores are very close to the scores reported in the paper.
        """
        duc2004 = self._load_multiple_summaries(_duc2004_file_path)
        centroid = self._load_summaries(_centroid_file_path)
        classy04 = self._load_summaries(_classy04_file_path)
        classy11 = self._load_summaries(_classy11_file_path)
        dpp = self._load_summaries(_dpp_file_path)
        freq_sum = self._load_summaries(_freq_sum_file_path)
        greedy_kl = self._load_summaries(_greedy_kl_file_path)
        icsi_summ = self._load_summaries(_icsi_summ_file_path)
        lexrank = self._load_summaries(_lexrank_file_path)
        occams_v = self._load_summaries(_occams_v_file_path)
        reg_sum = self._load_summaries(_reg_sum_file_path)
        submodular = self._load_summaries(_submodular_file_path)
        ts_sum = self._load_summaries(_ts_sum_file_path)

        rouge = Rouge(max_words=100)

        # Reported: 36.41, 7.97, 1.21
        metrics, _ = rouge.evaluate(centroid, duc2004)
        self.assertAlmostEqual(metrics['rouge-1']['recall'], 36.41, places=2)
        self.assertAlmostEqual(metrics['rouge-2']['recall'], 7.97, places=2)
        self.assertAlmostEqual(metrics['rouge-4']['recall'], 1.21, places=2)

        # Reported: 37.62, 8.96, 1.51
        metrics, _ = rouge.evaluate(classy04, duc2004)
        self.assertAlmostEqual(metrics['rouge-1']['recall'], 37.61, places=2)
        self.assertAlmostEqual(metrics['rouge-2']['recall'], 8.96, places=2)
        self.assertAlmostEqual(metrics['rouge-4']['recall'], 1.51, places=2)

        # Reported: 37.22, 9.20, 1.48
        metrics, _ = rouge.evaluate(classy11, duc2004)
        self.assertAlmostEqual(metrics['rouge-1']['recall'], 37.22, places=2)
        self.assertAlmostEqual(metrics['rouge-2']['recall'], 9.20, places=2)
        self.assertAlmostEqual(metrics['rouge-4']['recall'], 1.48, places=2)

        # Reported: 39.79, 9.62, 1.57
        metrics, _ = rouge.evaluate(dpp, duc2004)
        self.assertAlmostEqual(metrics['rouge-1']['recall'], 39.79, places=2)
        self.assertAlmostEqual(metrics['rouge-2']['recall'], 9.62, places=2)
        self.assertAlmostEqual(metrics['rouge-4']['recall'], 1.57, places=2)

        # Reported: 35.30, 8.11, 1.00
        metrics, _ = rouge.evaluate(freq_sum, duc2004)
        self.assertAlmostEqual(metrics['rouge-1']['recall'], 35.30, places=2)
        self.assertAlmostEqual(metrics['rouge-2']['recall'], 8.11, places=2)
        self.assertAlmostEqual(metrics['rouge-4']['recall'], 1.00, places=2)

        # Reported: 37.98, 8.53, 1.26
        metrics, _ = rouge.evaluate(greedy_kl, duc2004)
        self.assertAlmostEqual(metrics['rouge-1']['recall'], 37.98, places=2)
        self.assertAlmostEqual(metrics['rouge-2']['recall'], 8.53, places=2)
        self.assertAlmostEqual(metrics['rouge-4']['recall'], 1.26, places=2)

        # Reported: 38.41, 9.78, 1.73
        metrics, _ = rouge.evaluate(icsi_summ, duc2004)
        self.assertAlmostEqual(metrics['rouge-1']['recall'], 38.41, places=2)
        self.assertAlmostEqual(metrics['rouge-2']['recall'], 9.78, places=2)
        self.assertAlmostEqual(metrics['rouge-4']['recall'], 1.73, places=2)

        # Reported: 35.95, 7.47, 0.82
        metrics, _ = rouge.evaluate(lexrank, duc2004)
        self.assertAlmostEqual(metrics['rouge-1']['recall'], 35.95, places=2)
        self.assertAlmostEqual(metrics['rouge-2']['recall'], 7.47, places=2)
        self.assertAlmostEqual(metrics['rouge-4']['recall'], 0.82, places=2)

        # Reported: 38.50, 9.76, 1.33
        metrics, _ = rouge.evaluate(occams_v, duc2004)
        self.assertAlmostEqual(metrics['rouge-1']['recall'], 38.50, places=2)
        self.assertAlmostEqual(metrics['rouge-2']['recall'], 9.76, places=2)
        self.assertAlmostEqual(metrics['rouge-4']['recall'], 1.33, places=2)

        # Reported: 38.57, 9.75, 1.60
        metrics, _ = rouge.evaluate(reg_sum, duc2004)
        self.assertAlmostEqual(metrics['rouge-1']['recall'], 38.56, places=2)
        self.assertAlmostEqual(metrics['rouge-2']['recall'], 9.75, places=2)
        self.assertAlmostEqual(metrics['rouge-4']['recall'], 1.60, places=2)

        # Reported: 39.18, 9.35, 1.39
        metrics, _ = rouge.evaluate(submodular, duc2004)
        self.assertAlmostEqual(metrics['rouge-1']['recall'], 39.18, places=2)
        self.assertAlmostEqual(metrics['rouge-2']['recall'], 9.35, places=2)
        self.assertAlmostEqual(metrics['rouge-4']['recall'], 1.39, places=2)

        # Reported: 35.88, 8.15, 1.03
        metrics, _ = rouge.evaluate(ts_sum, duc2004)
        self.assertAlmostEqual(metrics['rouge-1']['recall'], 35.88, places=2)
        self.assertAlmostEqual(metrics['rouge-2']['recall'], 8.14, places=2)
        self.assertAlmostEqual(metrics['rouge-4']['recall'], 1.03, places=2)

    def test_multi_all(self):
        duc2004 = self._load_multiple_summaries(_duc2004_file_path)
        centroid = self._load_summaries(_centroid_file_path)
        classy04 = self._load_summaries(_classy04_file_path)
        classy11 = self._load_summaries(_classy11_file_path)

        rouge = Rouge(max_words=100)

        summaries_list = list(zip(*[centroid, classy04, classy11]))
        metrics_lists = rouge.score_multi_all(summaries_list, duc2004)
        metrics_lists = list(zip(*metrics_lists))
        metrics_list = [rouge.aggregate(metrics_list) for metrics_list in metrics_lists]

        expected_metrics_list = []
        for dataset in [centroid, classy04, classy11]:
            expected_metrics_list.append(rouge.aggregate(rouge.score_all(dataset, duc2004)))

        assert metrics_list == expected_metrics_list
