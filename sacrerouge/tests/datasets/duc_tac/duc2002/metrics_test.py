import os
import pytest
import unittest
from collections import defaultdict
from typing import Dict, List

from sacrerouge.data import Metrics
from sacrerouge.io import JsonlReader

_task1_metrics_file_path = 'datasets/duc-tac/duc2002/v1.0/task1.metrics.jsonl'
_task2_10_metrics_file_path = 'datasets/duc-tac/duc2002/v1.0/task2.10.metrics.jsonl'
_task2_50_metrics_file_path = 'datasets/duc-tac/duc2002/v1.0/task2.50.metrics.jsonl'
_task2_100_metrics_file_path = 'datasets/duc-tac/duc2002/v1.0/task2.100.metrics.jsonl'
_task2_200_metrics_file_path = 'datasets/duc-tac/duc2002/v1.0/task2.200.metrics.jsonl'


class TestDUC2002Metrics(unittest.TestCase):
    def _convert_to_dicts(self, metrics_list: List[Metrics]) -> Dict[str, Dict[str, Metrics]]:
        metrics_dicts = defaultdict(dict)
        for metrics in metrics_list:
            metrics_dicts[metrics.instance_id][metrics.summarizer_id] = metrics.metrics
        return metrics_dicts

    @pytest.mark.skipif(not os.path.exists(_task1_metrics_file_path), reason='DUC 2002 task 1 metrics file does not exist')
    def test_task1_system_level(self):
        summary_level_metrics = JsonlReader(_task1_metrics_file_path, Metrics).read()
        summary_level_metrics = self._convert_to_dicts(summary_level_metrics)

        # Check a few metrics to make sure they are equal to what's in the NIST files
        # results/abstracts.phase1/short.results.table
        assert summary_level_metrics['WSJ880912-0064']['16']['length_adjusted_coverage']['median'] == 0.007
        assert summary_level_metrics['AP890925-0124']['17']['length_adjusted_coverage']['mean'] == 0.333
        assert summary_level_metrics['FT923-5589']['19']['coverage']['mean'] == 0.417

    @pytest.mark.skipif(not os.path.exists(_task2_10_metrics_file_path), reason='DUC 2002 task 2 length 10 metrics file does not exist')
    def test_task2_length10__system_level(self):
        summary_level_metrics = JsonlReader(_task2_10_metrics_file_path, Metrics).read()
        summary_level_metrics = self._convert_to_dicts(summary_level_metrics)

        # Check a few metrics to make sure they are equal to what's in the NIST files
        # results/abstracts.phase1/short.results.table
        assert summary_level_metrics['d062']['29']['length_adjusted_coverage']['median'] == 0.0
        assert summary_level_metrics['d070']['25']['num_peer_units'] == 1
        assert summary_level_metrics['d109']['16']['coverage']['mean'] == 0.2

    @pytest.mark.skipif(not os.path.exists(_task2_50_metrics_file_path), reason='DUC 2002 task 2 length 50 metrics file does not exist')
    def test_task2_length50_system_level(self):
        summary_level_metrics = JsonlReader(_task2_50_metrics_file_path, Metrics).read()
        summary_level_metrics = self._convert_to_dicts(summary_level_metrics)

        # Check a few metrics to make sure they are equal to what's in the NIST files
        # results/abstracts.phase1/short.results.table
        assert summary_level_metrics['d109']['16']['length_adjusted_coverage']['median'] == 0.047
        assert summary_level_metrics['d112']['20']['peer_quality']['Q1'] == 1
        assert summary_level_metrics['d114']['19']['coverage']['mean'] == 0.25

    @pytest.mark.skipif(not os.path.exists(_task2_100_metrics_file_path), reason='DUC 2002 task 2 length 100 metrics file does not exist')
    def test_task2_length100_system_level(self):
        summary_level_metrics = JsonlReader(_task2_100_metrics_file_path, Metrics).read()
        summary_level_metrics = self._convert_to_dicts(summary_level_metrics)

        # Check a few metrics to make sure they are equal to what's in the NIST files
        # results/abstracts.phase1/short.results.table
        assert summary_level_metrics['d061']['16']['length_adjusted_coverage']['median'] == 0.003
        assert summary_level_metrics['d063']['25']['unmarked_units_related_to_subject'] == 0.8
        assert summary_level_metrics['d066']['C']['coverage']['mean'] == 0.523

    @pytest.mark.skipif(not os.path.exists(_task2_200_metrics_file_path), reason='DUC 2002 task 2 length 200 metrics file does not exist')
    def test_task2_length200_system_level(self):
        summary_level_metrics = JsonlReader(_task2_200_metrics_file_path, Metrics).read()
        summary_level_metrics = self._convert_to_dicts(summary_level_metrics)

        # Check a few metrics to make sure they are equal to what's in the NIST files
        # results/abstracts.phase1/short.results.table
        assert summary_level_metrics['d066']['20']['peer_quality']['Q5'] == 1
        assert summary_level_metrics['d069']['3']['num_peer_units'] == 7
        assert summary_level_metrics['d111']['28']['coverage']['mean'] == 0.411