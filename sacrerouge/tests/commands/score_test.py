import os
import pytest
import unittest
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
        with TemporaryDirectory() as temp_dir:
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

            assert len(instances) == len(metrics_list)
            for instance, metrics in zip(instances, metrics_list):
                assert metrics.instance_id == instance['instance_id']
                assert metrics.summarizer_id == instance['summarizer_id']
                assert metrics.summarizer_type == instance['summarizer_type']

                if metrics.summarizer_type == 'reference':
                    assert 'python-rouge-1_jk' in metrics.metrics
                    assert 'python-rouge-2_jk' in metrics.metrics
                else:
                    assert 'python-rouge-1' in metrics.metrics
                    assert 'python-rouge-2' in metrics.metrics
                    assert 'python-rouge-1_jk' in metrics.metrics
                    assert 'python-rouge-2_jk' in metrics.metrics
