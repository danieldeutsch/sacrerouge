import json
import subprocess
import pytest
import unittest

from sacrerouge.common import TemporaryDirectory
from sacrerouge.common.testing import MULTILING_METRICS


class TestCorrelate(unittest.TestCase):
    def test_correlate_reference(self):
        # This is a regression test for the "correlate" command. It does not test if it's accurate
        # TODO This needs to be a better test. There are too few summarization systems to get interesting
        # correlations
        with TemporaryDirectory() as temp_dir:
            command = [
                'python', '-m', 'sacrerouge', 'correlate',
                '--metrics-jsonl-files', MULTILING_METRICS,
                '--metrics', 'rouge-1_jk_precision', 'grade',
                '--summarizer-type', 'reference',
                '--output-file', f'{temp_dir}/correlations.json',
                '--silent'
            ]
            subprocess.run(command, check=True)
            correlations = json.load(open(f'{temp_dir}/correlations.json', 'r'))

            assert correlations['summary_level']['pearson']['r'] == pytest.approx(0.3333, abs=1e-4)
            assert correlations['summary_level']['spearman']['rho'] == pytest.approx(0.3333, abs=1e-4)
            assert correlations['summary_level']['kendall']['tau'] == pytest.approx(0.3333, abs=1e-4)
            assert correlations['summary_level']['num_summary_groups'] == 3

            assert correlations['system_level']['pearson']['r'] == pytest.approx(1.0, abs=1e-4)
            assert correlations['system_level']['spearman']['rho'] == pytest.approx(1.0, abs=1e-4)
            assert correlations['system_level']['kendall']['tau'] == pytest.approx(1.0, abs=1e-4)
            assert correlations['system_level']['num_summarizers'] == 2

            assert correlations['global']['pearson']['r'] == pytest.approx(0.6225273481541307, abs=1e-4)
            assert correlations['global']['spearman']['rho'] == pytest.approx(0.8285714285714287, abs=1e-4)
            assert correlations['global']['kendall']['tau'] == pytest.approx(0.7333333333333333, abs=1e-4)
            assert correlations['global']['num_summaries'] == 6

    def test_correlate_peer(self):
        # This is a regression test for the "correlate" command. It does not test if it's accurate
        # TODO This needs to be a better test. There are too few summarization systems to get interesting
        # correlations
        with TemporaryDirectory() as temp_dir:
            command = [
                'python', '-m', 'sacrerouge', 'correlate',
                '--metrics-jsonl-files', MULTILING_METRICS,
                '--metrics', 'rouge-1_precision', 'grade',
                '--summarizer-type', 'peer',
                '--output-file', f'{temp_dir}/correlations.json',
                '--silent'
            ]
            subprocess.run(command, check=True)
            correlations = json.load(open(f'{temp_dir}/correlations.json', 'r'))

            assert correlations['summary_level']['pearson']['r'] == pytest.approx(-0.3333, abs=1e-4)
            assert correlations['summary_level']['spearman']['rho'] == pytest.approx(-0.3333, abs=1e-4)
            assert correlations['summary_level']['kendall']['tau'] == pytest.approx(-0.3333, abs=1e-4)
            assert correlations['summary_level']['num_summary_groups'] == 3

            assert correlations['system_level']['pearson']['r'] == pytest.approx(-1.0, abs=1e-4)
            assert correlations['system_level']['spearman']['rho'] == pytest.approx(-1.0, abs=1e-4)
            assert correlations['system_level']['kendall']['tau'] == pytest.approx(-1.0, abs=1e-4)
            assert correlations['system_level']['num_summarizers'] == 2

            assert correlations['global']['pearson']['r'] == pytest.approx(-0.33056857901135617, abs=1e-4)
            assert correlations['global']['spearman']['rho'] == pytest.approx(-0.3768511731740915, abs=1e-4)
            assert correlations['global']['kendall']['tau'] == pytest.approx(-0.27602622373694163, abs=1e-4)
            assert correlations['global']['num_summaries'] == 6

    def test_correlate_all(self):
        # This is a regression test for the "correlate" command. It does not test if it's accurate
        with TemporaryDirectory() as temp_dir:
            command = [
                'python', '-m', 'sacrerouge', 'correlate',
                '--metrics-jsonl-files', MULTILING_METRICS,
                '--metrics', 'rouge-1_jk_precision', 'grade',
                '--summarizer-type', 'all',
                '--output-file', f'{temp_dir}/correlations.json',
                '--silent'
            ]
            subprocess.run(command, check=True)
            correlations = json.load(open(f'{temp_dir}/correlations.json', 'r'))

            assert correlations['summary_level']['pearson']['r'] == pytest.approx(0.4365526945989437, abs=1e-4)
            assert correlations['summary_level']['spearman']['rho'] == pytest.approx(0.3720759220056127, abs=1e-4)
            assert correlations['summary_level']['kendall']['tau'] == pytest.approx(0.1719691730561296, abs=1e-4)
            assert correlations['summary_level']['num_summary_groups'] == 3

            assert correlations['system_level']['pearson']['r'] == pytest.approx(0.28732601225892834, abs=1e-4)
            assert correlations['system_level']['spearman']['rho'] == pytest.approx(0.19999999999999998, abs=1e-4)
            assert correlations['system_level']['kendall']['tau'] == pytest.approx(0.0, abs=1e-4)
            assert correlations['system_level']['num_summarizers'] == 4

            assert correlations['global']['pearson']['r'] == pytest.approx(0.34183806349510004, abs=1e-4)
            assert correlations['global']['spearman']['rho'] == pytest.approx(0.4035707976004214, abs=1e-4)
            assert correlations['global']['kendall']['tau'] == pytest.approx(0.28603877677367767, abs=1e-4)
            assert correlations['global']['num_summaries'] == 12

    def test_all_summary_level_correlations(self):
        # This is a regression test for the "correlate" command. It does not test if it's accurate
        with TemporaryDirectory() as temp_dir:
            command = [
                'python', '-m', 'sacrerouge', 'correlate',
                '--metrics-jsonl-files', MULTILING_METRICS,
                '--metrics', 'rouge-1_jk_precision', 'grade',
                '--summarizer-type', 'all',
                '--output-file', f'{temp_dir}/correlations.json',
                '--silent',
                '--summary-level-correlations-output', f'{temp_dir}/summary-level.json'
            ]
            subprocess.run(command, check=True)

            # Check the original correlations
            correlations = json.load(open(f'{temp_dir}/correlations.json', 'r'))

            assert correlations['summary_level']['pearson']['r'] == pytest.approx(0.4365526945989437, abs=1e-4)
            assert correlations['summary_level']['spearman']['rho'] == pytest.approx(0.3720759220056127, abs=1e-4)
            assert correlations['summary_level']['kendall']['tau'] == pytest.approx(0.1719691730561296, abs=1e-4)
            assert correlations['summary_level']['num_summary_groups'] == 3

            assert correlations['system_level']['pearson']['r'] == pytest.approx(0.28732601225892834, abs=1e-4)
            assert correlations['system_level']['spearman']['rho'] == pytest.approx(0.19999999999999998, abs=1e-4)
            assert correlations['system_level']['kendall']['tau'] == pytest.approx(0.0, abs=1e-4)
            assert correlations['system_level']['num_summarizers'] == 4

            assert correlations['global']['pearson']['r'] == pytest.approx(0.34183806349510004, abs=1e-4)
            assert correlations['global']['spearman']['rho'] == pytest.approx(0.4035707976004214, abs=1e-4)
            assert correlations['global']['kendall']['tau'] == pytest.approx(0.28603877677367767, abs=1e-4)
            assert correlations['global']['num_summaries'] == 12

            # Check the individual summary-level correlations
            summary_level = json.load(open(f'{temp_dir}/summary-level.json', 'r'))
            assert summary_level['pearson'] == pytest.approx([0.3216337604513384, 0.38969747442783453, 0.598326848917658], abs=1e-4)
            assert summary_level['spearman'] == pytest.approx([0.6000000000000001, 0.316227766016838, 0.19999999999999998], abs=1e-4)
            assert summary_level['kendall'] == pytest.approx([0.3333333333333334, 0.18257418583505539, 0.0], abs=1e-4)