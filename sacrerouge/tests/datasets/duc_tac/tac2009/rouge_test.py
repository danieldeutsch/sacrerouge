import os
import pytest
import unittest
from typing import List

from sacrerouge.data import EvalInstance, Metrics
from sacrerouge.data.dataset_readers import ReferenceBasedDatasetReader
from sacrerouge.io import JsonlReader
from sacrerouge.metrics import Rouge
from sacrerouge.commands.score import score_instances

_summaries_file_path = 'datasets/duc-tac/tac2009/v1.0/task1.A-B.summaries.jsonl'
_metrics_file_path = 'datasets/duc-tac/tac2009/v1.0/task1.A-B.metrics.jsonl'


class TestTAC2009Rouge(unittest.TestCase):
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

    @pytest.mark.skipif(not os.path.exists(_summaries_file_path), reason='TAC 2009 summaries file does not exist')
    @pytest.mark.skipif(not os.path.exists(_metrics_file_path), reason='TAC 2009 metrics file does not exist')
    def test_rouge(self):
        # Test the first several instances in the TAC 2009 data to ensure that
        # our computation of ROUGE matches the values released by NIST
        instances = ReferenceBasedDatasetReader().read(_summaries_file_path)
        metrics_list = JsonlReader(_metrics_file_path, Metrics).read()
        # The LCS metrics do not match because the summaries NIST ran on were not sentence-tokenized,
        # which seems to have a very large effect on the scores. We have sentence-tokenized the summaries.
        metric_names = ['rouge-1', 'rouge-2', 'rouge-3', 'rouge-4', 'rouge-su4']
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
                assert actual_metrics.metrics[metric] == expected_metrics.metrics[metric]
                assert actual_metrics.metrics[metric + '_jk'] == expected_metrics.metrics[metric + '_jk']

        actual_metrics_dicts = score_instances(reference_instances[:num_to_check], [rouge])
        for expected_metrics in reference_metrics[:num_to_check]:
            instance_id = expected_metrics.instance_id
            summarizer_id = expected_metrics.summarizer_id
            actual_metrics = actual_metrics_dicts[instance_id][summarizer_id]

            for metric in metric_names:
                assert actual_metrics.metrics[metric + '_jk'] == expected_metrics.metrics[metric + '_jk']
