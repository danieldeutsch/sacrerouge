import os
import pytest
import unittest
from collections import defaultdict
from subprocess import PIPE, Popen

from sacrerouge.common import TemporaryDirectory
from sacrerouge.common.testing import FIXTURES_ROOT
from sacrerouge.data import Metrics
from sacrerouge.io import JsonlReader

_summaries_file_path = 'datasets/duc-tac/tac2008/v1.0/task1.A.summaries.jsonl'
_config_file_path = f'{FIXTURES_ROOT}/configs/score.json'


class TestScore(unittest.TestCase):
    @pytest.mark.skipif(not os.path.exists(_summaries_file_path), reason='TAC 2008 summaries file does not exist')
    def test_score(self):
        with TemporaryDirectory(root='.', persist=True) as temp_dir:
            output_file = f'{temp_dir}/metrics.jsonl'
            command = [
                'python', '-m', 'sacrerouge', 'score',
                _config_file_path,
                output_file
            ]

            process = Popen(command, stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()

            instances = JsonlReader(_summaries_file_path).read()
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
            assert metrics_dicts['d0801-A']['0'].metrics == {
                'python-rouge-1': {
                    'precision': 29.444444444444446,
                    'recall': 26.700251889168765,
                    'f1': 28.005284015852048
                },
                'python-rouge-2': {
                    'precision': 2.8089887640449436,
                    'recall': 2.5445292620865136,
                    'f1': 2.67022696929239
                },
                'python-rouge-1_jk': {
                    'precision': 29.444444444444443,
                    'recall': 26.719572295067344,
                    'f1': 28.015250464050713
                },
                'python-rouge-2_jk': {
                    'precision': 2.808988764044944,
                    'recall': 2.549772468714448,
                    'f1': 2.6730599647266313
                }
            }

            assert metrics_dicts['d0805-A']['B'].metrics == {
                'python-rouge-1_jk': {
                    'precision': 37.84722222222222,
                    'recall': 36.21262458471761,
                    'f1': 37.011884550084886
                },
                'python-rouge-2_jk': {
                    'precision': 9.12280701754386,
                    'recall': 8.724832214765101,
                    'f1': 8.919382504288166
                }
            }
