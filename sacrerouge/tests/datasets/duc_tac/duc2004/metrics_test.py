import os
import pytest
import unittest
from collections import defaultdict
from typing import Dict, List

from sacrerouge.data import Metrics
from sacrerouge.io import JsonlReader

_task2_metrics_file_path = 'datasets/duc-tac/duc2004/v1.0/task2.metrics.jsonl'
_task5_metrics_file_path = 'datasets/duc-tac/duc2004/v1.0/task5.metrics.jsonl'


class TestDUC2004Metrics(unittest.TestCase):
    def _convert_to_dicts(self, metrics_list: List[Metrics]) -> Dict[str, Dict[str, Metrics]]:
        metrics_dicts = defaultdict(dict)
        for metrics in metrics_list:
            metrics_dicts[metrics.instance_id][metrics.summarizer_id] = metrics.metrics
        return metrics_dicts

    @pytest.mark.skipif(not os.path.exists(_task2_metrics_file_path), reason='DUC 2004 task 2 metrics file does not exist')
    def test_task2_system_level(self):
        summary_level_metrics = JsonlReader(_task2_metrics_file_path, Metrics).read()
        summary_level_metrics = self._convert_to_dicts(summary_level_metrics)

        # Check a few metrics to make sure they are equal to what's in the NIST files
        # SEE/short.results.table2
        assert summary_level_metrics['d30001']['102']['peer_quality']['Q2'] == 1
        assert summary_level_metrics['d30005']['120']['coverage']['mean'] == 0.067
        assert summary_level_metrics['d30011']['A']['num_model_units'] == 11

    @pytest.mark.skipif(not os.path.exists(_task5_metrics_file_path), reason='DUC 2004 task 5 metrics file does not exist')
    def test_task5_system_level(self):
        summary_level_metrics = JsonlReader(_task5_metrics_file_path, Metrics).read()
        summary_level_metrics = self._convert_to_dicts(summary_level_metrics)

        # Check a few metrics to make sure they are equal to what's in the NIST files
        # SEE/short.results.table5
        assert summary_level_metrics['d132']['109']['peer_quality']['Q2'] == 1
        assert summary_level_metrics['d147']['5']['coverage']['mean'] == 0.160
        assert summary_level_metrics['d164']['F']['num_model_units'] == 8

        # Responsiveness/results.table.R
        assert summary_level_metrics['d132']['24']['responsiveness'] == 1
        assert summary_level_metrics['d200']['86']['responsiveness'] == 0
