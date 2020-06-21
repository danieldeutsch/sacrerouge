import json
import unittest
from collections import defaultdict
from subprocess import PIPE, Popen
from typing import Dict, List

from sacrerouge.common import TemporaryDirectory
from sacrerouge.common.testing import FIXTURES_ROOT, MULTILING_SUMMARIES
from sacrerouge.data import Metrics
from sacrerouge.io import JsonlReader

_config_file_path = f'{FIXTURES_ROOT}/configs/evaluate.json'
_numeric_config_file_path = f'{FIXTURES_ROOT}/configs/evaluate-numeric.json'


class TestMetricCommand(unittest.TestCase):
    def _check_macro_default(self, macro: Dict) -> None:
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

    def _check_micro_list_default(self, micro_list: List[Metrics]) -> None:
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

    def _check_macro_arguments(self, macro: Dict) -> None:
        assert macro['metrics'] == {
            'python-rouge-3': {
              'precision': 3.8408974398855293,
              'recall': 3.879200450421004,
              'f1': 3.8496095259110024
            },
            'python-rouge-l': {
              'precision': 27.622060602200875,
              'recall': 27.547088418712146,
              'f1': 27.50970881170657
            }
        }

    def _check_micro_list_arguments(self, micro_list: List[Metrics]) -> None:
        instances = JsonlReader(MULTILING_SUMMARIES).read()

        assert len(micro_list) == len(instances)
        for micro, instance in zip(micro_list, instances):
            assert micro.instance_id == instance['instance_id']
            assert micro.summarizer_id == instance['summarizer_id']
            assert micro.summarizer_type == instance['summarizer_type']

        assert micro_list[0].metrics == {
            'python-rouge-3': {
                'precision': 3.0952380952380953,
                'recall': 3.110047846889952,
                'f1': 3.1026252983293556
            },
            'python-rouge-l': {
                'precision': 20.657276995305164,
                'recall': 20.754716981132077,
                'f1': 20.705882352941174
            }
        }
        assert micro_list[11].metrics == {
            'python-rouge-3': {
                'precision': 4.273504273504273,
                'recall': 3.816793893129771,
                'f1': 4.03225806451613
            },
                'python-rouge-l': {
                'precision': 28.15126050420168,
                'recall': 25.18796992481203,
                'f1': 26.58730158730159
            }
        }

    def test_evaluate_default(self):
        # I manually ran evaluate with these parameters and this method checks to make sure
        # those values are equal to the output here
        with TemporaryDirectory() as temp_dir:
            macro_file = f'{temp_dir}/macro.json'
            micro_file = f'{temp_dir}/micro.jsonl'
            command = [
                'python', '-m', 'sacrerouge', 'python-rouge', 'evaluate',
                macro_file, micro_file,
                '--dataset-reader', 'reference-based',
                '--input-files', MULTILING_SUMMARIES,
                '--silent'
            ]

            process = Popen(command, stdout=PIPE, stderr=PIPE)
            process.communicate()

            macro_metrics = json.load(open(macro_file, 'r'))
            micro_metrics_list = JsonlReader(micro_file, Metrics).read()

            self._check_macro_default(macro_metrics)
            self._check_micro_list_default(micro_metrics_list)

    def test_evaluate_arguments(self):
        # I manually ran evaluate with these parameters and this method checks to make sure
        # those values are equal to the output here
        with TemporaryDirectory() as temp_dir:
            macro_file = f'{temp_dir}/macro.json'
            micro_file = f'{temp_dir}/micro.jsonl'
            command = [
                'python', '-m', 'sacrerouge', 'python-rouge', 'evaluate',
                macro_file, micro_file,
                '--ngram_orders', '[3]',
                '--use_porter_stemmer', 'false',
                '--remove_stopwords', 'true',
                '--compute_rouge_l', 'true',
                '--dataset-reader', 'reference-based',
                '--input-files', MULTILING_SUMMARIES,
                '--silent'
            ]

            process = Popen(command, stdout=PIPE, stderr=PIPE)
            process.communicate()

            macro_metrics = json.load(open(macro_file, 'r'))
            micro_metrics_list = JsonlReader(micro_file, Metrics).read()

            self._check_macro_arguments(macro_metrics)
            self._check_micro_list_arguments(micro_metrics_list)

    def test_score_default(self):
        with TemporaryDirectory() as temp_dir:
            # I manually ran the scoring function with these parameters, and this test makes sure
            # those are equal to the output here
            output_file = f'{temp_dir}/metrics.jsonl'
            command = [
                'python', '-m', 'sacrerouge', 'python-rouge', 'score',
                output_file,
                '--dataset-reader', 'reference-based',
                '--input-files', MULTILING_SUMMARIES,
                '--silent'
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

            assert metrics_dicts['M000']['1'].metrics == {
                'python-rouge-1': {
                  'precision': 41.699867197875164,
                  'recall': 40.516129032258064,
                  'f1': 41.09947643979057
                },
                'python-rouge-2': {
                  'precision': 10.533333333333333,
                  'recall': 10.233160621761659,
                  'f1': 10.38107752956636
                },
                'python-rouge-1_jk': {
                  'precision': 41.699867197875164,
                  'recall': 40.514662613316766,
                  'f1': 41.098355761265616
                },
                'python-rouge-2_jk': {
                  'precision': 10.533333333333333,
                  'recall': 10.226158358122346,
                  'f1': 10.3773782079838
                }
            }

            assert metrics_dicts['M001']['B'].metrics == {
                'python-rouge-1_jk': {
                  'precision': 51.59362549800797,
                  'recall': 51.18577075098815,
                  'f1': 51.3888888888889
                },
                'python-rouge-2_jk': {
                  'precision': 20.4,
                  'recall': 20.238095238095237,
                  'f1': 20.318725099601597
                }
            }

    def test_score_arguments(self):
        with TemporaryDirectory() as temp_dir:
            # I manually ran the scoring function with these parameters, and this test makes sure
            # those are equal to the output here
            output_file = f'{temp_dir}/metrics.jsonl'
            command = [
                'python', '-m', 'sacrerouge', 'python-rouge', 'score',
                output_file,
                '--dataset-reader', 'reference-based',
                '--input-files', MULTILING_SUMMARIES,
                '--ngram_orders', '[3]',
                '--use_porter_stemmer', 'false',
                '--remove_stopwords', 'true',
                '--compute_rouge_l', 'true',
                '--dataset-reader', 'reference-based',
                '--silent'
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
                    assert 'python-rouge-3_jk' in metrics.metrics
                    assert 'python-rouge-l_jk' in metrics.metrics
                else:
                    assert 'python-rouge-3' in metrics.metrics
                    assert 'python-rouge-l' in metrics.metrics
                    assert 'python-rouge-3_jk' in metrics.metrics
                    assert 'python-rouge-l_jk' in metrics.metrics

            assert metrics_dicts['M000']['1'].metrics == {
                'python-rouge-3': {
                    'precision': 3.0952380952380953,
                    'recall': 3.110047846889952,
                    'f1': 3.1026252983293556
                },
                'python-rouge-l': {
                    'precision': 20.657276995305164,
                    'recall': 20.754716981132077,
                    'f1': 20.705882352941174
                },
                'python-rouge-3_jk': {
                    'precision': 3.095238095238095,
                    'recall': 3.073768703921825,
                    'f1': 3.0843425372732653
                },
                'python-rouge-l_jk': {
                    'precision': 20.657276995305164,
                    'recall': 20.72789236755767,
                    'f1': 20.69018908745478
                }
            }

            assert metrics_dicts['M001']['B'].metrics == {
                'python-rouge-3_jk': {
                    'precision': 3.75,
                    'recall': 3.4615384615384617,
                    'f1': 3.6
                },
                'python-rouge-l_jk': {
                    'precision': 33.60655737704918,
                    'recall': 31.060606060606062,
                    'f1': 32.28346456692913
                }
            }