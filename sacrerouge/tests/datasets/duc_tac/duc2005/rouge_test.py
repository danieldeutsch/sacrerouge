import os
import pytest
import unittest
from typing import List

from sacrerouge.data import EvalInstance, Metrics
from sacrerouge.data.dataset_readers import ReferenceBasedDatasetReader
from sacrerouge.io import JsonlReader
from sacrerouge.metrics import Rouge
from sacrerouge.commands.score import score_instances

_summaries_file_path = 'datasets/duc-tac/duc2005/v1.0/task1.summaries.jsonl'
_metrics_file_path = 'datasets/duc-tac/duc2005/v1.0/task1.metrics.jsonl'


class TestDUC2005Rouge(unittest.TestCase):
    def _filter_by_type(self,
                        instances: List[EvalInstance],
                        metrics_list: List[Metrics],
                        summarizer_type: str):
        filtered_instances = []
        filtered_metrics = []
        for instance, metrics in zip(instances, metrics_list):
            if instance.summarizer_type == summarizer_type:
                filtered_instances.append(instance)
                filtered_metrics.append(metrics)
        return filtered_instances, filtered_metrics

    @pytest.mark.skipif(not os.path.exists(_summaries_file_path), reason='DUC 2005 task 1 summaries file does not exist')
    @pytest.mark.skipif(not os.path.exists(_metrics_file_path), reason='DUC 2005 task 1 metrics file does not exist')
    def test_rouge(self):
        # Test the first several instances in the DUC 2005 data to ensure that
        # our computation of ROUGE matches the values released by NIST. In this year,
        # they did not release the raw output for the non-jackknifing runs, so
        # we cannot compare those scores
        instances = ReferenceBasedDatasetReader(_summaries_file_path).read()
        metrics_list = JsonlReader(_metrics_file_path, Metrics).read()
        metric_names = ['rouge-1', 'rouge-2', 'rouge-3', 'rouge-4', 'rouge-l', 'rouge-su4', 'rouge-w-1.2']
        submetrics = ['precision', 'recall', 'f1']
        rouge = Rouge(max_ngram=4,
                      use_porter_stemmer=True,
                      remove_stopwords=False,
                      compute_rouge_l=True,
                      skip_bigram_gap_length=4,
                      wlcs_weight=1.2)

        peer_instances, peer_metrics = self._filter_by_type(instances, metrics_list, 'peer')
        reference_instances, reference_metrics = self._filter_by_type(instances, metrics_list, 'reference')

        num_to_check = 25
        actual_metrics_dicts = score_instances(peer_instances[:num_to_check], [rouge])
        for expected_metrics in peer_metrics[:num_to_check]:
            instance_id = expected_metrics.instance_id
            summarizer_id = expected_metrics.summarizer_id
            actual_metrics = actual_metrics_dicts[instance_id][summarizer_id]

            for metric in metric_names:
                for submetric in submetrics:
                    assert actual_metrics.metrics[metric + '_jk'] == expected_metrics.metrics[metric + '_jk']

        actual_metrics_dicts = score_instances(reference_instances[:num_to_check], [rouge])
        for expected_metrics in reference_metrics[:num_to_check]:
            instance_id = expected_metrics.instance_id
            summarizer_id = expected_metrics.summarizer_id
            actual_metrics = actual_metrics_dicts[instance_id][summarizer_id]

            for metric in metric_names:
                for submetric in submetrics:
                    assert actual_metrics.metrics[metric + '_jk'] == expected_metrics.metrics[metric + '_jk']
