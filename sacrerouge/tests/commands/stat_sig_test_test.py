import json
import subprocess
import unittest
from typing import Any, Dict

from sacrerouge.common import TemporaryDirectory
from sacrerouge.commands.stat_sig_test import run_wilcoxon_tests
from sacrerouge.common.testing.util import sacrerouge_command_exists


class TestStatisticalSignifianceTest(unittest.TestCase):
    """
    In scipy 1.4.1, the only method to calculate the p-value is through a normal approximation. In 1.5.2, they
    added an exact calculation for samples smaller than 25 by default. These unit tests test a sample size of 3, and
    therefore the change from 1.4.1 to 1.5.2 results in a different p-value. The tests here are written
    to check the results against scipy 1.5.2.
    """
    def setUp(self) -> None:
        self.correlations_A = {
            'pearson': {'A': 0.72, 'B': 0.14, 'C': 0.84, 'D': 0.98, 'E': 0.88},
            'spearman': {'A': 0.04, 'B': 0.32, 'C': 0.54, 'D': 0.18},
        }
        self.correlations_B = {
            'pearson': {'A': 0.24, 'B': 0.75, 'C': 0.34, 'D': 0.34, 'E': 0.22},
            'spearman': {'A': 0.98, 'B': 0.86, 'C': 0.77, 'E': 0.53},
            'kendall': {'A': 0.34, 'B': 0.88}
        }

    def _verify_results(self, results: Dict[str, Any]):
        assert results['alternative'] == 'two-sided'
        assert results['pearson']['n'] == 5
        assert results['pearson']['statistic'] == 3.0
        assert results['pearson']['p_value'] == 0.3125

        assert results['spearman']['n'] == 3
        assert results['spearman']['statistic'] == 0.0
        assert results['spearman']['p_value'] == 0.25

        assert 'kendall' not in results

    def test_command_exists(self):
        assert sacrerouge_command_exists(['stat-sig-test'])

    def test_run_wilcoxon_tests(self):
        # This is a regression test and does not test for accuracy
        results = run_wilcoxon_tests(self.correlations_A, self.correlations_B)
        self._verify_results(results)

    def test_command_line(self):
        # This is a regression test and does not test for accuracy
        with TemporaryDirectory() as temp_dir:
            with open(f'{temp_dir}/A.json', 'w') as out:
                out.write(json.dumps(self.correlations_A))
            with open(f'{temp_dir}/B.json', 'w') as out:
                out.write(json.dumps(self.correlations_B))

            command = [
                'python', '-m', 'sacrerouge', 'stat-sig-test',
                '--summary-level-correlations-A', f'{temp_dir}/A.json',
                '--summary-level-correlations-B', f'{temp_dir}/B.json',
                '--output-file', f'{temp_dir}/results.json',
                '--silent'
            ]
            subprocess.run(command, check=True)
            results = json.load(open(f'{temp_dir}/results.json', 'r'))
            self._verify_results(results)