import os
import pytest
import unittest
from collections import defaultdict
from typing import Dict, List

from sacrerouge.data import Metrics
from sacrerouge.io import JsonlReader


_en_file_path = 'datasets/multiling/multiling2011/en.metrics.jsonl'
_fr_file_path = 'datasets/multiling/multiling2011/fr.metrics.jsonl'


class TestMultiLing2011Metrics(unittest.TestCase):
    def _convert_to_dicts(self, metrics_list: List[Metrics]) -> Dict[str, Dict[str, Metrics]]:
        metrics_dicts = defaultdict(dict)
        for metrics in metrics_list:
            metrics_dicts[metrics.instance_id][metrics.summarizer_id] = metrics.metrics
        return metrics_dicts

    @pytest.mark.skipif(not os.path.exists(_en_file_path), reason='MultiLing 2011 English data does not exist')
    def test_en_summary_level(self):
        # Test a few random metrics to ensure the data was parsed correctly
        metrics_list = JsonlReader(_en_file_path, Metrics).read()
        metrics_dicts = self._convert_to_dicts(metrics_list)

        assert metrics_dicts['M004']['1']['rouge-1']['precision'] == pytest.approx(50.525, abs=1e-3)
        assert metrics_dicts['M004']['1']['rouge-1']['recall'] == pytest.approx(50.459, abs=1e-3)
        assert metrics_dicts['M004']['1']['rouge-1']['f1'] == pytest.approx(50.492, abs=1e-3)

        assert metrics_dicts['M009']['2']['rouge-2']['precision'] == pytest.approx(17.647, abs=1e-3)
        assert metrics_dicts['M009']['2']['rouge-2']['recall'] == pytest.approx(18.072, abs=1e-3)
        assert metrics_dicts['M009']['2']['rouge-2']['f1'] == pytest.approx(17.857, abs=1e-3)

        assert metrics_dicts['M002']['5']['MeMoG'] == pytest.approx(0.32643265, abs=1e-4)
        assert metrics_dicts['M004']['3']['MeMoG'] == pytest.approx(0.57679360, abs=1e-4)

        assert metrics_dicts['M000']['1']['grade'] == [2, 3, 3]
        assert metrics_dicts['M006']['4']['grade'] == [1, 3, 1]

        assert metrics_dicts['M000']['3']['length_aware_grade'] == [2.88, 3.83, 3.83]
        assert metrics_dicts['M006']['4']['length_aware_grade'] == [1.00, 3.00, 1.00]

    @pytest.mark.skipif(not os.path.exists(_fr_file_path), reason='MultiLing 2011 French data does not exist')
    def test_fr_summary_level(self):
        # Test a few random metrics to ensure the data was parsed correctly
        metrics_list = JsonlReader(_fr_file_path, Metrics).read()
        metrics_dicts = self._convert_to_dicts(metrics_list)

        assert metrics_dicts['M004']['1']['rouge-1']['precision'] == pytest.approx(42.791, abs=1e-3)
        assert metrics_dicts['M004']['1']['rouge-1']['recall'] == pytest.approx(44.753, abs=1e-3)
        assert metrics_dicts['M004']['1']['rouge-1']['f1'] == pytest.approx(43.750, abs=1e-3)

        assert metrics_dicts['M009']['2']['rouge-2']['precision'] == pytest.approx(17.770, abs=1e-3)
        assert metrics_dicts['M009']['2']['rouge-2']['recall'] == pytest.approx(17.813, abs=1e-3)
        assert metrics_dicts['M009']['2']['rouge-2']['f1'] == pytest.approx(17.791, abs=1e-3)

        assert metrics_dicts['M002']['5']['MeMoG'] == pytest.approx(0.24885254, abs=1e-4)
        assert metrics_dicts['M004']['3']['MeMoG'] == pytest.approx(0.46445730, abs=1e-4)

        assert metrics_dicts['M000']['1']['grade'] == [3, 1, 3]
        assert metrics_dicts['M006']['4']['grade'] == [1, 3, 3]

        assert metrics_dicts['M000']['3']['length_aware_grade'] == [2.73, 2.73, 3.63]
        assert metrics_dicts['M006']['4']['length_aware_grade'] == [1.00, 3.00, 3.00]
