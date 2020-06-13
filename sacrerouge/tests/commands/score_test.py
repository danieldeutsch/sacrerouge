import os
import pytest
import unittest
from collections import defaultdict
from subprocess import PIPE, Popen

from sacrerouge.common import TemporaryDirectory
from sacrerouge.common.testing import FIXTURES_ROOT, MULTILING_SUMMARIES
from sacrerouge.data import Metrics
from sacrerouge.io import JsonlReader

_config_file_path = f'{FIXTURES_ROOT}/configs/score.json'


class TestScore(unittest.TestCase):
    def test_score(self):
        with TemporaryDirectory() as temp_dir:
            # Runs a regression test for the "score" command
            output_file = f'{temp_dir}/metrics.jsonl'
            command = [
                'python', '-m', 'sacrerouge', 'score',
                _config_file_path,
                output_file
            ]

            process = Popen(command, stdout=PIPE, stderr=PIPE)
            process.communicate()

            instances = JsonlReader(MULTILING_SUMMARIES).read()
            metrics_list = JsonlReader(output_file, Metrics).read()
            metrics_dicts = defaultdict(dict)

            assert len(instances) == len(metrics_list)
            for instance, metrics in zip(instances, metrics_list):
                assert metrics.instance_id == instance['instance_id']
                assert metrics.summarizer_id == instance['summarizer_id']
                assert metrics.summarizer_type == instance['summarizer_type']
                metrics_dicts[metrics.instance_id][metrics.summarizer_id] = metrics

                if metrics.summarizer_type == 'reference':
                    assert 'python-rouge-1_jk' in metrics.metrics
                    assert 'python-rouge-2_jk' in metrics.metrics
                else:
                    assert 'python-rouge-1' in metrics.metrics
                    assert 'python-rouge-2' in metrics.metrics
                    assert 'python-rouge-1_jk' in metrics.metrics
                    assert 'python-rouge-2_jk' in metrics.metrics

            # Test a couple of instances. I did not check to see if these are correct,
            # but the test will check if the results have changed
            assert metrics_dicts['M000']['1'].metrics == {
                "python-rouge-1": {
                  "precision": 41.699867197875164,
                  "recall": 40.516129032258064,
                  "f1": 41.09947643979057
                },
                "python-rouge-2": {
                  "precision": 10.533333333333333,
                  "recall": 10.233160621761659,
                  "f1": 10.38107752956636
                },
                "python-rouge-1_jk": {
                  "precision": 41.699867197875164,
                  "recall": 40.514662613316766,
                  "f1": 41.098355761265616
                },
                "python-rouge-2_jk": {
                  "precision": 10.533333333333333,
                  "recall": 10.226158358122346,
                  "f1": 10.3773782079838
                }
            }

            assert metrics_dicts['M001']['B'].metrics == {
                "python-rouge-1_jk": {
                  "precision": 51.59362549800797,
                  "recall": 51.18577075098815,
                  "f1": 51.3888888888889
                },
                "python-rouge-2_jk": {
                  "precision": 20.4,
                  "recall": 20.238095238095237,
                  "f1": 20.318725099601597
                }
            }
