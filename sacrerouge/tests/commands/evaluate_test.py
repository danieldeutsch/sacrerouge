import json
import unittest
from subprocess import PIPE, Popen
from typing import Dict, List

from sacrerouge.common import TemporaryDirectory
from sacrerouge.common.testing import FIXTURES_ROOT, MULTILING_SUMMARIES
from sacrerouge.data import Metrics
from sacrerouge.io import JsonlReader

_config_file_path = f'{FIXTURES_ROOT}/configs/evaluate.json'


class TestEvaluate(unittest.TestCase):
    def _check_macro(self, macro: Dict) -> None:
        assert macro['metrics'] == {
            'python-rouge-1': {
                'precision': 47.288299019868255,
                'recall': 46.36412967789611,
                'f1': 46.734012277932806
            },
            'python-rouge-2': {
                'precision': 16.625951207280107,
                'recall': 16.30045341659763,
                'f1': 16.430312150593775
            }
        }

    def _check_micro_list(self, micro_list: List[Metrics]) -> None:
        instances = JsonlReader(MULTILING_SUMMARIES).read()

        assert len(micro_list) == len(instances)
        for micro, instance in zip(micro_list, instances):
            assert micro.instance_id == instance['instance_id']
            assert micro.summarizer_id == instance['summarizer_id']
            assert micro.summarizer_type == instance['summarizer_type']

        assert micro_list[0].metrics == {
            'python-rouge-1': {
                'precision': 41.699867197875164,
                'recall': 40.516129032258064,
                'f1': 41.09947643979057
            },
            'python-rouge-2': {
                'precision': 10.533333333333333,
                'recall': 10.233160621761659,
                'f1': 10.38107752956636
            }
        }
        assert micro_list[11].metrics == {
            'python-rouge-1': {
                'precision': 45.34412955465587,
                'recall': 44.71057884231537,
                'f1': 45.0251256281407
            },
            'python-rouge-2': {
                'precision': 15.24390243902439,
                'recall': 15.030060120240481,
                'f1': 15.136226034308779
            }
        }

    def test_evaluate(self):
        # This is a regresion test and does not ensure correctness
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
            process.communicate()

            macro_metrics = json.load(open(macro_file, 'r'))
            micro_metrics_list = JsonlReader(micro_file, Metrics).read()

            self._check_macro(macro_metrics)
            self._check_micro_list(micro_metrics_list)
