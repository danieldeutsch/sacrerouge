import os
import pytest
import unittest
from typing import Any, Dict, List

from sacrerouge.io import JsonlReader
from sacrerouge.metrics import Rouge
from sacrerouge.score import run_jackknifing

_summaries_file_path = 'datasets/duc-tac/tac2009/v1.0/task1.A-B.summaries.jsonl'
_metrics_file_path = 'datasets/duc-tac/tac2009/v1.0/task1.A-B.metrics.jsonl'


class TestTAC2009Rouge(unittest.TestCase):
    def _filter_by_type(self,
                        instances: List[Dict[str, Any]],
                        metrics_list: List[Dict[str, Any]],
                        summarizer_type: str):
        filtered_instances = []
        filtered_metrics = []
        for instance, metrics in zip(instances, metrics_list):
            if instance['summarizer_type'] == summarizer_type:
                filtered_instances.append(instance)
                filtered_metrics.append(metrics)
        return filtered_instances, filtered_metrics

    @pytest.mark.skipif(not os.path.exists(_summaries_file_path), reason='TAC 2009 summaries file does not exist')
    @pytest.mark.skipif(not os.path.exists(_metrics_file_path), reason='TAC 2009 metrics file does not exist')
    def test_rouge(self):
        # Test the first several instances in the TAC 2009 data to ensure that
        # our computation of ROUGE matches the values released by NIST
        instances = JsonlReader(_summaries_file_path).read()
        metrics_list = JsonlReader(_metrics_file_path).read()
        # TODO: the LCS metrics do not come close to matching
        metric_names = ['rouge-1', 'rouge-2', 'rouge-3', 'rouge-4', 'rouge-su4']
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
        for instance, metrics in zip(peer_instances[:num_to_check], peer_metrics[:num_to_check]):
            summary = instance['summary']['text']
            references = [reference['text'] for reference in instance['references']]
            actual_metrics = rouge.score(summary, references)

            for metric in metric_names:
                for submetric in submetrics:
                    assert actual_metrics[metric][submetric] == metrics['metrics'][metric][submetric]

            actual_metrics = run_jackknifing([rouge], summary, references)
            for metric in metric_names:
                for submetric in submetrics:
                    assert actual_metrics[metric + '_jk'][submetric] == metrics['metrics'][metric + '_jk'][submetric]

        for instance, metrics in zip(reference_instances[:num_to_check], reference_metrics[:num_to_check]):
            summary = instance['summary']['text']
            references = [reference['text'] for reference in instance['references']]
            actual_metrics = rouge.score(summary, references)

            for metric in metric_names:
                for submetric in submetrics:
                    assert actual_metrics[metric][submetric] == metrics['metrics'][metric + '_jk'][submetric]
