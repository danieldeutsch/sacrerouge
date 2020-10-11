import os
import pytest

from sacrerouge.common.testing import FIXTURES_ROOT
from sacrerouge.common.testing.metric_test_cases import ReferenceBasedMetricTestCase
from sacrerouge.common.testing.util import load_references, load_summaries
from sacrerouge.metrics import Rouge

_duc2004_file_path = 'datasets/duc-tac/duc2004/v1.0/task2.jsonl'
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


class TestRouge(ReferenceBasedMetricTestCase):
    @pytest.mark.skipif(not os.path.exists(_duc2004_file_path), reason='DUC 2004 data does not exist')
    @pytest.mark.skipif(not os.path.exists(_centroid_file_path), reason='Hong 2014 data does not exist')
    def test_hong2014(self):
        """
        Tests to ensure that the Rouge scores for the summaries from Hong et al. 2014
        (http://www.lrec-conf.org/proceedings/lrec2014/pdf/1093_Paper.pdf) do not
        change. The hard-coded scores are very close to the scores reported in the paper.
        """
        duc2004 = load_references(_duc2004_file_path)
        centroid = load_summaries(_centroid_file_path)
        classy04 = load_summaries(_classy04_file_path)
        classy11 = load_summaries(_classy11_file_path)
        dpp = load_summaries(_dpp_file_path)
        freq_sum = load_summaries(_freq_sum_file_path)
        greedy_kl = load_summaries(_greedy_kl_file_path)
        icsi_summ = load_summaries(_icsi_summ_file_path)
        lexrank = load_summaries(_lexrank_file_path)
        occams_v = load_summaries(_occams_v_file_path)
        reg_sum = load_summaries(_reg_sum_file_path)
        submodular = load_summaries(_submodular_file_path)
        ts_sum = load_summaries(_ts_sum_file_path)

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

    def test_rouge(self):
        # This is a regression test, not necessarily a test for correctness
        metric = Rouge(max_ngram=2, compute_rouge_l=True)
        expected_output = [
            {
                'rouge-1': {'recall': 40.516000000000005, 'precision': 41.699999999999996, 'f1': 41.099000000000004},
                'rouge-2': {'recall': 10.233, 'precision': 10.533, 'f1': 10.381},
                'rouge-l': {'recall': 36.258, 'precision': 37.317, 'f1': 36.78}
            },
            {
                'rouge-1': {'recall': 48.258, 'precision': 47.765, 'f1': 48.010000000000005},
                'rouge-2': {'recall': 19.301, 'precision': 19.103, 'f1': 19.200999999999997},
                'rouge-l': {'recall': 44.774, 'precision': 44.317, 'f1': 44.544}
            },
            {
                'rouge-1': {'recall': 49.416, 'precision': 48.659, 'f1': 49.035000000000004},
                'rouge-2': {'recall': 16.406000000000002, 'precision': 16.154, 'f1': 16.279},
                'rouge-l': {'recall': 45.72, 'precision': 45.019, 'f1': 45.367000000000004}
            },
            {
                'rouge-1': {'recall': 44.466, 'precision': 44.038, 'f1': 44.251000000000005},
                'rouge-2': {'recall': 11.891, 'precision': 11.776, 'f1': 11.833},
                'rouge-l': {'recall': 40.971000000000004, 'precision': 40.577000000000005, 'f1': 40.772999999999996}
            },
            {
                'rouge-1': {'recall': 42.403999999999996, 'precision': 41.473, 'f1': 41.933},
                'rouge-2': {'recall': 10.477, 'precision': 10.245999999999999, 'f1': 10.36},
                'rouge-l': {'recall': 37.649, 'precision': 36.822, 'f1': 37.230999999999995}
            },
            {
                'rouge-1': {'recall': 43.857, 'precision': 43.061, 'f1': 43.455},
                'rouge-2': {'recall': 13.395000000000001, 'precision': 13.150999999999998, 'f1': 13.272},
                'rouge-l': {'recall': 40.555, 'precision': 39.818, 'f1': 40.183}},
            {
                'rouge-1': {'recall': 52.39, 'precision': 51.568999999999996, 'f1': 51.976},
                'rouge-2': {'recall': 20.4, 'precision': 20.079, 'f1': 20.238},
                'rouge-l': {'recall': 47.211, 'precision': 46.471000000000004, 'f1': 46.838}},
            {
                'rouge-1': {'recall': 51.186, 'precision': 51.593999999999994, 'f1': 51.388999999999996},
                'rouge-2': {'recall': 20.238, 'precision': 20.4, 'f1': 20.319000000000003},
                'rouge-l': {'recall': 46.64, 'precision': 47.012, 'f1': 46.825}},
            {
                'rouge-1': {'recall': 38.635999999999996, 'precision': 52.641000000000005, 'f1': 44.564},
                'rouge-2': {'recall': 13.691, 'precision': 18.681, 'f1': 15.801000000000002},
                'rouge-l': {'recall': 35.829, 'precision': 48.815999999999995, 'f1': 41.326}
            },
            {
                'rouge-1': {'recall': 51.73799999999999, 'precision': 51.6, 'f1': 51.669},
                'rouge-2': {'recall': 23.49, 'precision': 23.427, 'f1': 23.458000000000002},
                'rouge-l': {'recall': 49.332, 'precision': 49.2, 'f1': 49.266}
            },
            {
                'rouge-1': {'recall': 48.79, 'precision': 48.016, 'f1': 48.4},
                'rouge-2': {'recall': 21.053, 'precision': 20.717, 'f1': 20.884},
                'rouge-l': {'recall': 47.782000000000004, 'precision': 47.024, 'f1': 47.4}
            },
            {
                'rouge-1': {'recall': 44.711, 'precision': 45.344, 'f1': 45.025},
                'rouge-2': {'recall': 15.03, 'precision': 15.244, 'f1': 15.136},
                'rouge-l': {'recall': 44.112, 'precision': 44.737, 'f1': 44.422}
            }
        ]
        super().assert_expected_output(metric, expected_output)

    def test_rouge_order_invariant(self):
        metric = Rouge(max_words=100)
        self.assert_order_invariant(metric)

    def test_commandline_runs(self):
        self.assert_commandline_runs('rouge')