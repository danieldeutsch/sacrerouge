import os
import pytest
import unittest
from collections import defaultdict
from typing import Dict, List

from sacrerouge.data import Metrics
from sacrerouge.io import JsonlReader

_metrics_file_path = 'datasets/duc-tac/duc2006/v1.0/task1.metrics.jsonl'


class TestDUC2006Metrics(unittest.TestCase):
    def _convert_to_dicts(self, metrics_list: List[Metrics]) -> Dict[str, Dict[str, Metrics]]:
        metrics_dicts = defaultdict(dict)
        for metrics in metrics_list:
            metrics_dicts[metrics.instance_id][metrics.summarizer_id] = metrics.metrics
        return metrics_dicts

    @pytest.mark.skipif(not os.path.exists(_metrics_file_path), reason='DUC 2006 metrics file does not exist')
    def test_system_level(self):
        summary_level_metrics = JsonlReader(_metrics_file_path, Metrics).read()
        summary_level_metrics = self._convert_to_dicts(summary_level_metrics)

        # Check a few metrics to make sure they are equal to what's in the NIST files
        # DUC2006pyramiddata/scoring/2006_modified_scores.txt
        assert summary_level_metrics['d0603']['32']['modified_pyramid_score'] == pytest.approx(0.1048, 1e-2)
        assert summary_level_metrics['d0616']['10']['modified_pyramid_score'] == pytest.approx(0.3103, 1e-2)
        assert summary_level_metrics['d0628']['6']['modified_pyramid_score'] == pytest.approx(0.0769, 1e-2)

        assert summary_level_metrics['d0603']['32']['num_scus'] == 6
        assert summary_level_metrics['d0616']['10']['num_scus'] == 7
        assert summary_level_metrics['d0628']['6']['num_scus'] == 2

        assert summary_level_metrics['d0603']['32']['num_repetitions'] == 0
        assert summary_level_metrics['d0616']['10']['num_repetitions'] == 0
        assert summary_level_metrics['d0628']['6']['num_repetitions'] == 0

        assert summary_level_metrics['d0603']['32']['content_responsiveness'] == 3
        assert summary_level_metrics['d0616']['10']['content_responsiveness'] == 4
        assert summary_level_metrics['d0628']['6']['content_responsiveness'] == 2
