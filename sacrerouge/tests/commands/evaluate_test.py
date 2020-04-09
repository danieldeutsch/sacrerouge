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
        # I did not check these for correctness (other than the correctness of PythonRouge
        # itself), but this should catch if anything changes
        assert macro['metrics'] == {
            'python-rouge-1': {
                'precision': 34.728410791962965,
                'recall': 34.36775110547158,
                'f1': 34.488188700511316
            },
            'python-rouge-2': {
                'precision': 8.185740108131075,
                'recall': 8.132737972371066,
                'f1': 8.146449089653041
            }
        }

    def _check_micro_list(self, micro_list: List[Metrics]) -> None:
        instances = JsonlReader(_summaries_file_path).read()

        assert len(micro_list) == len(instances)
        for micro, instance in zip(micro_list, instances):
            assert micro.instance_id == instance['instance_id']
            assert micro.summarizer_id == instance['summarizer_id']
            assert micro.summarizer_type == instance['summarizer_type']

        # Test a couple of cases. Again, I did not manually test these, but they
        # will catch if anything changes
        assert micro_list[1].metrics == {
            'python-rouge-1': {
                'precision': 30.412371134020617,
                'recall': 29.72292191435768,
                'f1': 30.06369426751592
            },
            'python-rouge-2': {
                'precision': 2.604166666666667,
                'recall': 2.5445292620865136,
                'f1': 2.5740025740025736
            }
        }
        assert micro_list[2848].metrics == {
            'python-rouge-1': {
                'precision': 29.207920792079207,
                'recall': 28.780487804878046,
                'f1': 28.99262899262899
            },
            'python-rouge-2': {
                'precision': 8.5,
                'recall': 8.374384236453201,
                'f1': 8.436724565756823
            }
        }

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
