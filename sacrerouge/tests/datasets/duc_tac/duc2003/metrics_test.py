import os
import pytest
import unittest
from collections import defaultdict
from typing import Dict, List

from sacrerouge.data import Metrics
from sacrerouge.io import JsonlReader

_task1_metrics_file_path = 'datasets/duc-tac/duc2003/v1.0/task1.metrics.jsonl'
_task2_metrics_file_path = 'datasets/duc-tac/duc2003/v1.0/task2.metrics.jsonl'
_task3_metrics_file_path = 'datasets/duc-tac/duc2003/v1.0/task3.metrics.jsonl'
_task4_metrics_file_path = 'datasets/duc-tac/duc2003/v1.0/task4.metrics.jsonl'


class TestDUC2003Metrics(unittest.TestCase):
    def _convert_to_dicts(self, metrics_list: List[Metrics]) -> Dict[str, Dict[str, Metrics]]:
        metrics_dicts = defaultdict(dict)
        for metrics in metrics_list:
            metrics_dicts[metrics.instance_id][metrics.summarizer_id] = metrics.metrics
        return metrics_dicts

    @pytest.mark.skipif(not os.path.exists(_task1_metrics_file_path), reason='DUC 2003 task 1 metrics file does not exist')
    def test_task1_system_level(self):
        summary_level_metrics = JsonlReader(_task1_metrics_file_path, Metrics).read()
        summary_level_metrics = self._convert_to_dicts(summary_level_metrics)

        # Check a few metrics to make sure they are equal to what's in the NIST files
        # results/original.results.corrected.improved.withPenaltyForExcess/results.table1
        assert summary_level_metrics['NYT19990925.0263']['10']['length_adjusted_coverage']['median'] == 0.267
        assert summary_level_metrics['NYT19981204.0331']['17']['coverage']['mean'] == 0.2
        assert summary_level_metrics['XIE19980211.0079']['18']['coverage']['median'] == 0.0

        # results/results.table.U.paired
        assert summary_level_metrics['NYT19990925.0263']['7']['usefulness'] == [2, 1]
        assert summary_level_metrics['APW19981005.0718']['H']['usefulness'] == [3, 2]
        assert summary_level_metrics['APW19981123.0532']['25']['usefulness'] == [1, 1]

    @pytest.mark.skipif(not os.path.exists(_task2_metrics_file_path), reason='DUC 2003 task 2 metrics file does not exist')
    def test_task2_system_level(self):
        summary_level_metrics = JsonlReader(_task2_metrics_file_path, Metrics).read()
        summary_level_metrics = self._convert_to_dicts(summary_level_metrics)

        # Check a few metrics to make sure they are equal to what's in the NIST files
        # results/original.results.corrected.improved.withPenaltyForExcess/results.table2
        assert summary_level_metrics['d30003']['10']['peer_quality']['Q1'] == 1
        assert summary_level_metrics['d30034']['13']['coverage']['std'] == 0.316
        assert summary_level_metrics['d31013']['15']['peer_quality']['Q2'] == 2

    @pytest.mark.skipif(not os.path.exists(_task3_metrics_file_path), reason='DUC 2003 task 3 metrics file does not exist')
    def test_task3_system_level(self):
        summary_level_metrics = JsonlReader(_task3_metrics_file_path, Metrics).read()
        summary_level_metrics = self._convert_to_dicts(summary_level_metrics)

        # Check a few metrics to make sure they are equal to what's in the NIST files
        # results/original.results.corrected.improved.withPenaltyForExcess/results.table3
        assert summary_level_metrics['d111']['17']['peer_quality']['Q4'] == 1
        assert summary_level_metrics['d123']['16']['unmarked_units_related_to_subject'] == 1.0
        assert summary_level_metrics['d125']['B']['num_peer_units'] == 6

    @pytest.mark.skipif(not os.path.exists(_task4_metrics_file_path), reason='DUC 2003 task 4 metrics file does not exist')
    def test_task4_system_level(self):
        summary_level_metrics = JsonlReader(_task4_metrics_file_path, Metrics).read()
        summary_level_metrics = self._convert_to_dicts(summary_level_metrics)

        # Check a few metrics to make sure they are equal to what's in the NIST files
        # results/original.results.corrected.improved.withPenaltyForExcess/results.table4
        assert summary_level_metrics['d305']['10']['length_adjusted_coverage']['std'] == 0.079
        assert summary_level_metrics['d365']['14']['unmarked_units_related_to_subject'] == 1.0
        assert summary_level_metrics['d382']['C']['num_peer_units'] == 6

        # results/results.table.R.paired
        assert summary_level_metrics['d305']['10']['responsiveness'] == [4, 2]
        assert summary_level_metrics['d326']['E']['responsiveness'] == [4, 3]
        assert summary_level_metrics['d432']['19']['responsiveness'] == [1, 1]
