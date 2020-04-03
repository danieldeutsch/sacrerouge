import json
import os
import subprocess
import pytest
import unittest

from sacrerouge.common import TemporaryDirectory

_metrics_file_path = 'datasets/duc-tac/tac2008/v1.0/task1.A-B.metrics.jsonl'


class TestCorrelate(unittest.TestCase):
    # (https://tac.nist.gov//publications/2008/additional.papers/update_summ_overview08.proceedings.pdf)
    @pytest.mark.skipif(not os.path.exists(_metrics_file_path), reason='TAC 2008 metrics file does not exist')
    def test_dang_2008_table_6_example(self):
        with TemporaryDirectory() as temp_dir:
            command = [
                'python', '-m', 'sacrerouge' 'correlate',
                '--metrics-jsonl-files', _metrics_file_path,
                '--metrics', 'overall_responsiveness', 'linguistic_quality',
                '--summarizer-type', 'reference',
                '--output-file', f'{temp_dir}/correlations.json',
                '--silent'
            ]
            subprocess.run(command, check=True)
            correlations = json.load(open(f'{temp_dir}/correlations.json', 'r'))
            assert correlations['system_level']['spearman']['rho'] == pytest.approx(0.910, 1e-2)
            assert correlations['system_level']['pearson']['r'] == pytest.approx(0.778, 1e-2)
            assert correlations['system_level']['num_summarizers'] == 8
