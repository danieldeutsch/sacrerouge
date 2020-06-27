import argparse
import unittest
from typing import List, Tuple

from sacrerouge.common.arguments import add_metric_arguments, get_metric_from_arguments, get_dataset_reader_from_argument
from sacrerouge.data.dataset_readers import DatasetReader
from sacrerouge.metrics import Metric


@DatasetReader.register('faked')
class _FakedDatasetReader(DatasetReader):
    def __init__(self, x: int = 4):
        super().__init__()
        self.x = x


@Metric.register('faked')
class _FakedMetric(Metric):
    def __init__(self,
                 a,
                 b: bool,
                 c: int,
                 d: float = 3.5,
                 e: str = None,
                 f: bool = False,
                 g: bool = True,
                 h: List[str] = None,
                 i: List[str] = list(['a', 'b'])):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.e = e
        self.f = f
        self.g = g
        self.h = h
        self.i = i


class TestArguments(unittest.TestCase):
    def test_get_dataset_reader_from_argument(self):
        reader = get_dataset_reader_from_argument('faked')
        assert isinstance(reader, _FakedDatasetReader)
        assert reader.x == 4

        reader = get_dataset_reader_from_argument('{"type": "faked", "x": 3}')
        assert isinstance(reader, _FakedDatasetReader)
        assert reader.x == 3

    def test_add_metric_arguments(self):
        argp = argparse.ArgumentParser()
        add_metric_arguments(argp, _FakedMetric)

        dest_to_action = {action.dest: action for action in argp._actions}
        assert len(dest_to_action) == 10  # Extra argument is for "help"

        action = dest_to_action['a']
        assert action.type == str
        assert action.default is None
        assert action.required is True

        # Boolean type is a function which is not checked here
        action = dest_to_action['b']
        assert action.default is None
        assert action.required is True

        action = dest_to_action['c']
        assert action.type == int
        assert action.default is None
        assert action.required is True

        action = dest_to_action['d']
        assert action.type == float
        assert action.default == 3.5
        assert action.required is False

        action = dest_to_action['e']
        assert action.type == str
        assert action.default == None
        assert action.required is False

        # Boolean type is a function which is not checked here
        action = dest_to_action['f']
        assert action.default == False
        assert action.required is False

        # Boolean type is a function which is not checked here
        action = dest_to_action['g']
        assert action.default is True
        assert action.required is False

        action = dest_to_action['h']
        assert action.type == str
        assert action.default == None
        assert action.required is False

        action = dest_to_action['i']
        assert action.type == str
        assert action.default == '["a", "b"]'
        assert action.required is False

    def test_get_metric_from_arguments(self):
        argp = argparse.ArgumentParser()
        add_metric_arguments(argp, _FakedMetric)

        # All arguments provided and defaults overridden
        args = argp.parse_args([
            '--a', 'test',
            '--b', 'true',
            '--c', '4',
            '--d', '1.2',
            '--e', 'hello',
            '--f', 'true',
            '--g', 'false',
            '--h', '["1", "2"]',
            '--i', '["3", "4"]'
        ])
        metric = get_metric_from_arguments(_FakedMetric, args)
        assert isinstance(metric, _FakedMetric)
        assert metric.a == 'test'
        assert metric.b is True
        assert metric.c == 4
        assert metric.d == 1.2
        assert metric.e == 'hello'
        assert metric.f is True
        assert metric.g is False
        assert metric.h == ['1', '2']
        assert metric.i == ['3', '4']

        # Only required arguments
        args = argp.parse_args([
            '--a', 'test',
            '--b', 'true',
            '--c', '4'
        ])
        metric = get_metric_from_arguments(_FakedMetric, args)
        assert isinstance(metric, _FakedMetric)
        assert metric.a == 'test'
        assert metric.b is True
        assert metric.c == 4
        assert metric.d == 3.5
        assert metric.e is None
        assert metric.f is False
        assert metric.g is True
        assert metric.h is None
        assert metric.i == ['a', 'b']