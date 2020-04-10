import os
import pytest
import unittest
from collections import defaultdict
from typing import Dict, List

from sacrerouge.data import Metrics
from sacrerouge.io import JsonlReader

_metrics_file_path = 'datasets/duc-tac/duc2005/v1.0/task1.metrics.jsonl'


class TestDUC2005Metrics(unittest.TestCase):
    def _convert_to_dicts(self, metrics_list: List[Metrics]) -> Dict[str, Dict[str, Metrics]]:
        metrics_dicts = defaultdict(dict)
        for metrics in metrics_list:
            metrics_dicts[metrics.instance_id][metrics.summarizer_id] = metrics.metrics
        return metrics_dicts

    @pytest.mark.skipif(not os.path.exists(_metrics_file_path), reason='DUC 2005 metrics file does not exist')
    def test_system_level(self):
        summary_level_metrics = JsonlReader(_metrics_file_path, Metrics).read()
        summary_level_metrics = self._convert_to_dicts(summary_level_metrics)

        # Check a few metrics to make sure they are equal to what's in the NIST files
        # Pyramid/DUC2005/processed_pans.txt
        assert summary_level_metrics['d311']['14']['pyramid_score'] == pytest.approx(0.5521, 1e-2)
        assert summary_level_metrics['d345']['31']['pyramid_score'] == 0.0
        assert summary_level_metrics['d400']['A']['pyramid_score'] == pytest.approx(0.5094, 1e-2)

        assert summary_level_metrics['d311']['14']['modified_pyramid_score'] == pytest.approx(0.3869, 1e-2)
        assert summary_level_metrics['d345']['31']['modified_pyramid_score'] == 0.0
        assert summary_level_metrics['d400']['A']['modified_pyramid_score'] == pytest.approx(0.4576, 1e-2)

        assert summary_level_metrics['d311']['14']['num_scus'] == 10
        assert summary_level_metrics['d345']['31']['num_scus'] == 0
        assert summary_level_metrics['d400']['A']['num_scus'] == 23

        assert summary_level_metrics['d311']['14']['num_repetitions'] == 7
        assert summary_level_metrics['d345']['31']['num_repetitions'] == 0
        assert summary_level_metrics['d400']['A']['num_repetitions'] == 7

        assert summary_level_metrics['d311']['14']['responsiveness'] == 3
        assert summary_level_metrics['d345']['31']['responsiveness'] == 1
        assert summary_level_metrics['d400']['A']['responsiveness'] == 5
