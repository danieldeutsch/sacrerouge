import json
import os
import pytest
import unittest
from subprocess import PIPE, Popen
from typing import Dict, List

from sacrerouge.common import TemporaryDirectory
from sacrerouge.common.testing import FIXTURES_ROOT
from sacrerouge.data import Metrics
from sacrerouge.io import JsonlReader

_summaries_file_path = 'datasets/duc-tac/tac2008/v1.0/task1.A.summaries.jsonl'
_config_file_path = f'{FIXTURES_ROOT}/configs/evaluate.json'


class TestEvaluate(unittest.TestCase):
    def _check_macro(self, macro: Dict) -> None:
        assert len(macro['metrics']) == 2
        assert 'python-rouge-1' in macro['metrics']
        assert 'python-rouge-2' in macro['metrics']

    def _check_micro_list(self, micro_list: List[Metrics]) -> None:
        instances = JsonlReader(_summaries_file_path).read()

        assert len(micro_list) == len(instances)
        for micro, instance in zip(micro_list, instances):
            assert micro.instance_id == instance['instance_id']
            assert micro.summarizer_id == instance['summarizer_id']
            assert micro.summarizer_type == instance['summarizer_type']

    @pytest.mark.skipif(not os.path.exists(_summaries_file_path), reason='TAC 2008 summaries file does not exist')
    def test_evaluate(self):
        with TemporaryDirectory() as temp_dir:
            macro_file = f'{temp_dir}/macro.json'
            micro_file = f'{temp_dir}/micro.jsonl'
            command = [
                'python', '-m', 'sacrerouge', 'evaluate',
                _config_file_path,
                macro_file,
                micro_file,
                '--silent'
            ]

            process = Popen(command, stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()

            macro_metrics = json.load(open(macro_file, 'r'))
            micro_metrics_list = JsonlReader(micro_file, Metrics).read()

            self._check_macro(macro_metrics)
            self._check_micro_list(micro_metrics_list)
