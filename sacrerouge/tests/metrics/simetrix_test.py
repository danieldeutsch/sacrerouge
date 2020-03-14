import os
import pytest
import unittest
from collections import defaultdict

from sacrerouge.common.testing import FIXTURES_ROOT
from sacrerouge.compute_correlation import aggregate_metrics
from sacrerouge.io import JsonlReader
from sacrerouge.metrics import SIMetrix

_simetrix_jar = 'external/SIMetrix/simetrix.jar'
_instances_file_path = f'{FIXTURES_ROOT}/data/simetrix/instances.jsonl'
_summary_metrics_file_path = f'{FIXTURES_ROOT}/data/simetrix/metrics.summary-level.jsonl'
_system_metrics_file_path = f'{FIXTURES_ROOT}/data/simetrix/metrics.system-level.jsonl'


class TestSIMetrix(unittest.TestCase):
    def _create_metrics_map(self, metrics_list):
        metrics_map = defaultdict(dict)
        for metrics in metrics_list:
            instance_id = metrics['instance_id']
            summarizer_id = metrics['summarizer_id']
            metrics_map[instance_id][summarizer_id] = metrics['metrics']
        return metrics_map

    def _create_metrics_map_from_pairs(self, instances, metrics_list):
        metrics_map = defaultdict(dict)
        for instance, metrics in zip(instances, metrics_list):
            instance_id = instance['instance_id']
            summarizer_id = instance['summarizer_id']
            metrics_map[instance_id][summarizer_id] = metrics
        return metrics_map

    def _create_instances(self, instances, metrics_list):
        new_instances = []
        for instance, metrics in zip(instances, metrics_list):
            new_instances.append({
                'instance_id': instance['instance_id'],
                'summarizer_id': instance['summarizer_id'],
                'metrics': metrics
            })
        return new_instances

    @pytest.mark.skipif(not os.path.exists(_simetrix_jar), reason='SIMetrix jar does not exist')
    @pytest.mark.skipif(not os.path.exists(_instances_file_path), reason='SIMetrix data does not exist')
    @pytest.mark.skipif(not os.path.exists(_summary_metrics_file_path), reason='SIMetrix data does not exist')
    @pytest.mark.skipif(not os.path.exists(_system_metrics_file_path), reason='SIMetrix data does not exist')
    def test_simetrix(self):
        instances = JsonlReader(_instances_file_path).read()
        summaries = [instance['summary'] for instance in instances]
        documents_list = [instance['documents'] for instance in instances]

        expected_summary_metrics_list = JsonlReader(_summary_metrics_file_path).read()
        expected_summary_metrics_dict = self._create_metrics_map(expected_summary_metrics_list)

        simetrix = SIMetrix()
        _, metrics_list = simetrix.score_all(summaries, documents_list)
        metrics_map = self._create_metrics_map_from_pairs(instances, metrics_list)

        assert len(expected_summary_metrics_dict) == len(metrics_map)
        for instance_id in metrics_map.keys():
            assert len(expected_summary_metrics_dict[instance_id]) == len(metrics_map[instance_id])
            for summarizer_id in metrics_map[instance_id].keys():
                assert len(expected_summary_metrics_dict[instance_id][summarizer_id]) == len(metrics_map[instance_id][summarizer_id])
                for name, value in metrics_map[instance_id][summarizer_id].items():
                    assert value == expected_summary_metrics_dict[instance_id][summarizer_id][name]

        expected_system_metrics_list = JsonlReader(_system_metrics_file_path).read()

        evaluation_instances = self._create_instances(instances, metrics_list)
        system_metrics_dict = aggregate_metrics(evaluation_instances, 'summarizer_id')

        assert len(system_metrics_dict) == len(expected_system_metrics_list)
        for expected_metrics in expected_system_metrics_list:
            summarizer_id = expected_metrics['summarizer_id']
            assert len(system_metrics_dict[summarizer_id]) == len(expected_metrics['metrics'])
            for name, value in system_metrics_dict[summarizer_id].items():
                assert value == pytest.approx(expected_metrics['metrics']['Avg' + name], abs=0.01)
