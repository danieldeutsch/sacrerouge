import itertools
import os
import pytest
import unittest

from sacrerouge.common.testing import FIXTURES_ROOT
from sacrerouge.io import JsonlReader
from sacrerouge.metrics import SIMetrix

_simetrix_jar = 'external/SIMetrix/simetrix.jar'
_instances_file_path = f'{FIXTURES_ROOT}/data/simetrix/instances.jsonl'
_summary_metrics_file_path = f'{FIXTURES_ROOT}/data/simetrix/metrics.summary-level.jsonl'
_system_metrics_file_path = f'{FIXTURES_ROOT}/data/simetrix/metrics.system-level.jsonl'


class TestSIMetrix(unittest.TestCase):
    def _setup_multi_all(self, instances):
        instance_id_to_index = {}
        summarizer_id_to_index = {}
        summaries_lists = []
        documents_lists = []

        instances = instances[:]
        instances.sort(key=lambda instance: instance['instance_id'])
        for i, (instance_id, group) in enumerate(itertools.groupby(instances, key=lambda instance: instance['instance_id'])):
            instance_id_to_index[instance_id] = i
            group = list(group)
            group.sort(key=lambda instance: instance['summarizer_id'])

            # Take the documents from the first instance
            first = group[0]
            documents_lists.append(first['documents'])

            # Add the summaries
            summaries_list = []
            for j, instance in enumerate(group):
                summarizer_id = instance['summarizer_id']
                summarizer_id_to_index[summarizer_id] = j
                summaries_list.append(instance['summary'])
            summaries_lists.append(summaries_list)

        return summaries_lists, documents_lists, instance_id_to_index, summarizer_id_to_index

    @pytest.mark.skipif(not os.path.exists(_simetrix_jar), reason='SIMetrix jar does not exist')
    @pytest.mark.skipif(not os.path.exists(_instances_file_path), reason='SIMetrix data does not exist')
    @pytest.mark.skipif(not os.path.exists(_summary_metrics_file_path), reason='SIMetrix data does not exist')
    def test_score_multi_all(self):
        instances = JsonlReader(_instances_file_path).read()
        summaries_lists, documents_lists, instance_id_to_index, summarizer_id_to_index = self._setup_multi_all(instances)

        simetrix = SIMetrix()
        metrics_lists = simetrix.score_multi_all(summaries_lists, documents_lists)
        for expected_metrics in JsonlReader(_summary_metrics_file_path).read():
            instance_index = instance_id_to_index[expected_metrics['instance_id']]
            summarizer_index = summarizer_id_to_index[expected_metrics['summarizer_id']]
            actual_metrics = metrics_lists[instance_index][summarizer_index]
            assert actual_metrics == expected_metrics['metrics']

    @pytest.mark.skipif(not os.path.exists(_simetrix_jar), reason='SIMetrix jar does not exist')
    @pytest.mark.skipif(not os.path.exists(_instances_file_path), reason='SIMetrix data does not exist')
    @pytest.mark.skipif(not os.path.exists(_system_metrics_file_path), reason='SIMetrix data does not exist')
    def test_evaluate(self):
        instances = JsonlReader(_instances_file_path).read()
        simetrix = SIMetrix()

        summarizer_id_to_metrics = {}
        for expected_metrics in JsonlReader(_system_metrics_file_path).read():
            summarizer_id = expected_metrics['summarizer_id']
            summarizer_id_to_metrics[summarizer_id] = expected_metrics

        instances.sort(key=lambda instance: instance['summarizer_id'])
        for summarizer_id, group in itertools.groupby(instances, key=lambda instance: instance['summarizer_id']):
            group = list(group)
            summaries = [member['summary'] for member in group]
            documents_list = [member['documents'] for member in group]
            actual_metrics, _ = simetrix.evaluate(summaries, documents_list)
            expected_metrics = summarizer_id_to_metrics[summarizer_id]['metrics']

            assert len(actual_metrics) == len(expected_metrics)
            for metric, value in actual_metrics.items():
                assert value == expected_metrics['Avg' + metric]
