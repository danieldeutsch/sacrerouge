import json
import os
import pytest
import subprocess
import unittest

from sacrerouge.common import TemporaryDirectory
from sacrerouge.common.testing.util import sacrerouge_command_exists

_metrics_file_path = 'datasets/duc-tac/tac2008/v1.0/task1.A-B.metrics.jsonl'


class TestStatisticalSignifianceTest(unittest.TestCase):
    def test_command_exists(self):
        assert sacrerouge_command_exists(['stat-sig-test'])

    @pytest.mark.skipif(not os.path.exists(_metrics_file_path), reason='TAC 2008 dataset does not exist')
    def test_correlate_reference(self):
        # We have to use the TAC 2008 data because the MultiLing data is too small for
        # the bootstrapping to work
        with TemporaryDirectory() as temp_dir:
            command = [
                'python', '-m', 'sacrerouge', 'stat-sig-test',
                '--metrics-jsonl-files', _metrics_file_path,
                '--dependent-metric', 'overall_responsiveness',
                '--metric-A', 'rouge-1_jk_precision',
                '--metric-B', 'rouge-2_jk_recall',
                '--summarizer-type', 'all',
                '--hypothesis-test', 'bootstrap-both',
                '--output-file', f'{temp_dir}/correlations.json',
                '--random-seed', '6',
                '--silent'
            ]
            subprocess.run(command, check=True)
            correlations = json.load(open(f'{temp_dir}/correlations.json', 'r'))

            assert correlations['dependent_metric'] == 'overall_responsiveness'
            assert correlations['metric_A'] == 'rouge-1_jk_precision'
            assert correlations['metric_B'] == 'rouge-2_jk_recall'
            assert correlations['summarizer_type'] == 'all'
            assert correlations['test_method'] == 'bootstrap-both'
            self.assertAlmostEqual(correlations['alpha'], 0.05, places=4)
            assert correlations['two_tailed'] is False
            assert correlations['H0'] == 'r(rouge-1_jk_precision, overall_responsiveness) <= r(rouge-2_jk_recall, overall_responsiveness)'
            assert correlations['H1'] == 'r(rouge-1_jk_precision, overall_responsiveness) > r(rouge-2_jk_recall, overall_responsiveness)'

            assert correlations['summary_level']['pearson']['pvalue'] == 0.829
            assert correlations['summary_level']['pearson']['is_significant'] is False
            assert correlations['summary_level']['spearman']['pvalue'] == 0.938
            assert correlations['summary_level']['spearman']['is_significant'] is False
            assert correlations['summary_level']['kendall']['pvalue'] == 0.929
            assert correlations['summary_level']['kendall']['is_significant'] is False

            assert correlations['system_level']['pearson']['pvalue'] == 0.603
            assert correlations['system_level']['pearson']['is_significant'] is False
            assert correlations['system_level']['spearman']['pvalue'] == 0.945
            assert correlations['system_level']['spearman']['is_significant'] is False
            assert correlations['system_level']['kendall']['pvalue'] == 0.977
            assert correlations['system_level']['kendall']['is_significant'] is False

            assert correlations['global']['pearson']['pvalue'] == 0.49
            assert correlations['global']['pearson']['is_significant'] is False
            assert correlations['global']['spearman']['pvalue'] == 0.831
            assert correlations['global']['spearman']['is_significant'] is False
            assert correlations['global']['kendall']['pvalue'] == 0.811
            assert correlations['global']['kendall']['is_significant'] is False