import os
import pytest
import unittest
from collections import defaultdict
from typing import Dict, List

from sacrerouge.data import Metrics
from sacrerouge.io import JsonlReader

_task1_metrics_file_path = 'datasets/duc-tac/duc2007/v1.0/task1.metrics.jsonl'
_task2_metrics_file_path = 'datasets/duc-tac/duc2007/v1.0/task2.A-B-C.metrics.jsonl'


class TestDUC2007Metrics(unittest.TestCase):
    def _convert_to_dicts(self, metrics_list: List[Metrics]) -> Dict[str, Dict[str, Metrics]]:
        metrics_dicts = defaultdict(dict)
        for metrics in metrics_list:
            metrics_dicts[metrics.instance_id][metrics.summarizer_id] = metrics.metrics
        return metrics_dicts

    @pytest.mark.skipif(not os.path.exists(_task1_metrics_file_path), reason='DUC 2007 task 1 metrics file does not exist')
    def test_task1_metrics(self):
        summary_level_metrics = JsonlReader(_task1_metrics_file_path, Metrics).read()
        summary_level_metrics = self._convert_to_dicts(summary_level_metrics)

        # Check a few metrics to make sure they are equal to what's in the NIST files. Unlike
        # the "system_level_test.py", these metrics don't have aggregated values in the NIST data,
        # so we just check to make sure a few of them were correctly parsed
        # mainPyramidEval/scoring/2007_modified_scores.txt
        assert summary_level_metrics['d0714']['23']['modified_pyramid_score'] == pytest.approx(0.3636, 1e-2)
        assert summary_level_metrics['d0710']['29']['modified_pyramid_score'] == pytest.approx(0.5062, 1e-2)
        assert summary_level_metrics['d0728']['2']['modified_pyramid_score'] == pytest.approx(0.04, 1e-2)

        assert summary_level_metrics['d0714']['23']['num_scus'] == 10
        assert summary_level_metrics['d0710']['29']['num_scus'] == 18
        assert summary_level_metrics['d0728']['2']['num_scus'] == 1

        assert summary_level_metrics['d0714']['23']['num_repetitions'] == 0
        assert summary_level_metrics['d0710']['29']['num_repetitions'] == 2
        assert summary_level_metrics['d0728']['2']['num_repetitions'] == 0

        assert summary_level_metrics['d0714']['23']['linguistic_quality']['Q1'] == 5
        assert summary_level_metrics['d0710']['29']['linguistic_quality']['Q1'] == 3
        assert summary_level_metrics['d0728']['2']['linguistic_quality']['Q1'] == 2

        assert summary_level_metrics['d0714']['23']['linguistic_quality']['Q2'] == 5
        assert summary_level_metrics['d0710']['29']['linguistic_quality']['Q2'] == 2
        assert summary_level_metrics['d0728']['2']['linguistic_quality']['Q2'] == 3

        assert summary_level_metrics['d0714']['23']['linguistic_quality']['Q3'] == 4
        assert summary_level_metrics['d0710']['29']['linguistic_quality']['Q3'] == 2
        assert summary_level_metrics['d0728']['2']['linguistic_quality']['Q3'] == 3

        assert summary_level_metrics['d0714']['23']['linguistic_quality']['Q4'] == 5
        assert summary_level_metrics['d0710']['29']['linguistic_quality']['Q4'] == 3
        assert summary_level_metrics['d0728']['2']['linguistic_quality']['Q4'] == 3

        assert summary_level_metrics['d0714']['23']['linguistic_quality']['Q5'] == 4
        assert summary_level_metrics['d0710']['29']['linguistic_quality']['Q5'] == 2
        assert summary_level_metrics['d0728']['2']['linguistic_quality']['Q5'] == 3

        assert summary_level_metrics['d0714']['23']['content_responsiveness'] == 3
        assert summary_level_metrics['d0710']['29']['content_responsiveness'] == 3
        assert summary_level_metrics['d0728']['2']['content_responsiveness'] == 4

    @pytest.mark.skipif(not os.path.exists(_task2_metrics_file_path), reason='DUC 2007 task 1 metrics file does not exist')
    def test_task2_metrics(self):
        summary_level_metrics = JsonlReader(_task2_metrics_file_path, Metrics).read()
        summary_level_metrics = self._convert_to_dicts(summary_level_metrics)

        # Check a few metrics to make sure they are equal to what's in the NIST files. Unlike
        # the "system_level_test.py", these metrics don't have aggregated values in the NIST data,
        # so we just check to make sure a few of them were correctly parsed
        # updateEval/Pyramid/scoring/2007_modified_scores.txt
        assert summary_level_metrics['d0703-A']['39']['modified_pyramid_score'] == pytest.approx(0.2857, 1e-2)
        assert summary_level_metrics['d0711-B']['45']['modified_pyramid_score'] == pytest.approx(0.2353, 1e-2)
        assert summary_level_metrics['d0726-C']['51']['modified_pyramid_score'] == pytest.approx(0.1739, 1e-2)

        assert summary_level_metrics['d0703-A']['39']['num_scus'] == 3
        assert summary_level_metrics['d0711-B']['45']['num_scus'] == 1
        assert summary_level_metrics['d0726-C']['51']['num_scus'] == 2

        assert summary_level_metrics['d0703-A']['39']['num_repetitions'] == 0
        assert summary_level_metrics['d0711-B']['45']['num_repetitions'] == 0
        assert summary_level_metrics['d0726-C']['51']['num_repetitions'] == 0

        assert summary_level_metrics['d0703-A']['39']['content_responsiveness'] == 2
        assert summary_level_metrics['d0711-B']['45']['content_responsiveness'] == 2
        assert summary_level_metrics['d0726-C']['51']['content_responsiveness'] == 2
