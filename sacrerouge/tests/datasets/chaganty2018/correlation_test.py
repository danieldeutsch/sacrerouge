import json
import os
import pytest
import subprocess
import unittest

from sacrerouge.common import TemporaryDirectory

_metrics_file_path = 'datasets/chaganty2018/metrics.jsonl'


class TestChaganty2018Correlation(unittest.TestCase):
    @pytest.mark.skipif(not os.path.exists(_metrics_file_path), reason='Chaganty 2018 metrics file does not exist')
    def test_correlation(self):
        with TemporaryDirectory() as temp_dir:
            command = [
                'python', '-m', 'sacrerouge.compute_correlation',
                '--metrics-jsonl-files', _metrics_file_path,
                '--metrics', 'chaganty2018_overall', 'chaganty2018_rouge-1_recall',
                '--summarizer-type', 'peer',
                '--output-file', f'{temp_dir}/correlations.json',
                '--silent'
            ]
            subprocess.run(command, check=True)
            correlations = json.load(open(f'{temp_dir}/correlations.json', 'r'))
            print(correlations)
            # assert correlations['system_level']['spearman']['rho'] == pytest.approx(0.910, 1e-2)
            # assert correlations['system_level']['pearson']['r'] == pytest.approx(0.778, 1e-2)
            # assert correlations['system_level']['num_summarizers'] == 4
