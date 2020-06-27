import json
import unittest
from subprocess import PIPE, Popen
from typing import Dict, List

from sacrerouge.common import TemporaryDirectory
from sacrerouge.common.testing import FIXTURES_ROOT, MULTILING_SUMMARIES
from sacrerouge.data import Metrics
from sacrerouge.io import JsonlReader

_config_file_path = f'{FIXTURES_ROOT}/configs/evaluate.json'
_numeric_config_file_path = f'{FIXTURES_ROOT}/configs/evaluate-numeric.json'


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
        # This is a regression test and does not ensure correctness
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

    def test_numeric_metric(self):
        with TemporaryDirectory() as temp_dir:
            macro_file = f'{temp_dir}/macro.json'
            micro_file = f'{temp_dir}/micro.jsonl'
            command = [
                'python', '-m', 'sacrerouge', 'evaluate',
                _numeric_config_file_path,
                macro_file,
                micro_file,
                '--silent'
            ]

            process = Popen(command, stdout=PIPE, stderr=PIPE)
            process.communicate()

            macro_metrics = json.load(open(macro_file, 'r'))
            micro_metrics_list = JsonlReader(micro_file, Metrics).read()

            assert macro_metrics == {'metrics': {'test': 45066}}

            assert len(micro_metrics_list) == 5
            assert micro_metrics_list[0].instance_id == 'D1'
            assert micro_metrics_list[1].instance_id == 'D1'
            assert micro_metrics_list[2].instance_id == 'D1'
            assert micro_metrics_list[3].instance_id == 'D1'
            assert micro_metrics_list[4].instance_id == 'D1'

            assert micro_metrics_list[0].summarizer_id == '1'
            assert micro_metrics_list[1].summarizer_id == '2'
            assert micro_metrics_list[2].summarizer_id == 'A'
            assert micro_metrics_list[3].summarizer_id == 'B'
            assert micro_metrics_list[4].summarizer_id == 'C'

            assert micro_metrics_list[0].summarizer_type == 'peer'
            assert micro_metrics_list[1].summarizer_type == 'peer'
            assert micro_metrics_list[2].summarizer_type == 'reference'
            assert micro_metrics_list[3].summarizer_type == 'reference'
            assert micro_metrics_list[4].summarizer_type == 'reference'

            assert micro_metrics_list[0].metrics == {'test': 1110}  # 1 * 10 + 1 * 100 + 1 * 1000
            assert micro_metrics_list[1].metrics == {'test': 2220}  # 2 * 10 + 2 * 100 + 2 * 1000
            assert micro_metrics_list[2].metrics == {'test': 11000}  # 10 * 100 + 10 * 1000
            assert micro_metrics_list[3].metrics == {'test': 101000}  # 100 * 10 + 100 * 1000
            assert micro_metrics_list[4].metrics == {'test': 110000}  # 1000 * 10 + 10000 * 100