import copy
import pytest
from typing import Dict, List, Optional, Union

ValueType = Union['MetricsDict', float, List[float]]


class MetricsDict(dict):
    def __init__(self, initial_dict: Optional[Union['MetricsDict', Dict]] = None) -> None:
        super().__init__()
        if initial_dict:
            initial_dict = copy.deepcopy(initial_dict)
            for key, value in initial_dict.items():
                self[key] = value

    def __setitem__(self, key: str, value: Union[ValueType, Dict]) -> None:
        # If it's a dictionary, we need to convert it to a MetricsDict
        if isinstance(value, dict):
            value_dict = MetricsDict()
            for k, v in value.items():
                value_dict[k] = v
            value = value_dict

        return dict.__setitem__(self, key, value)

    def __getitem__(self, key: str) -> ValueType:
        if not dict.__contains__(self, key):
            dict.__setitem__(self, key, MetricsDict())
        return dict.__getitem__(self, key)

    def flatten_keys(self) -> 'MetricsDict':
        def _recursive_iterate(metrics_dict: MetricsDict, prefix: List[str]):
            for key, value in metrics_dict.items():
                if isinstance(value, MetricsDict):
                    yield from _recursive_iterate(value, prefix + [key])
                else:
                    yield (prefix + [key], value)

        result = MetricsDict()
        for path, value in _recursive_iterate(self, []):
            name = '_'.join(path)
            result[name] = value
        return result

    def average_values(self) -> 'MetricsDict':
        result = MetricsDict()
        for key, value in self.items():
            if isinstance(value, MetricsDict):
                result[key] = value.average_values()
            elif isinstance(value, list):
                result[key] = sum(value) / len(value)
            else:
                result[key] = value
        return result

    def select_metrics(self, metrics: List[str]) -> 'MetricsDict':
        selected = MetricsDict()
        for metric in metrics:
            selected[metric] = self[metric]
        return selected

    def update(self, other: 'MetricsDict') -> None:
        for key, value in other.items():
            if key in self:
                if isinstance(self[key], MetricsDict) and isinstance(value, MetricsDict):
                    self[key].update(value)
                else:
                    self[key] = value
            else:
                self[key] = value

    def _add_to(self, target: 'MetricsDict') -> 'MetricsDict':
        # We created this method so that both __add__ and __radd__ can create
        # an intermediate cumulative MetricsDict and use this method to add to it.
        # Otherwise, it's impossible for __add__ to know if it's adding to the
        # cumulative MetricsDict or the other actual value.
        assert self.keys() == target.keys()
        for key, value in self.items():
            target[key] += value
        return target

    def __add__(self, other: 'MetricsDict') -> 'MetricsDict':
        assert self.keys() == other.keys()
        total = copy.deepcopy(other)
        return self._add_to(total)

    def __radd__(self, other: Union[int, 'MetricsDict']) -> 'MetricsDict':
        if other == 0:
            return copy.deepcopy(self)
        else:
            return self._add_to(other)

    def __truediv__(self, denominator: float) -> 'MetricsDict':
        result = MetricsDict()
        for key, value in self.items():
            result[key] = value / denominator
        return result

    def approx_equal(self, other: 'MetricsDict', rel=None, abs=None):
        if self.keys() != other.keys():
            return False
        for key in self.keys():
            value = self[key]
            other_value = other[key]
            if isinstance(value, MetricsDict) and isinstance(other_value, MetricsDict):
                if not value.approx_equal(other_value, rel=rel, abs=abs):
                    return False
            elif isinstance(value, (int, float)) and isinstance(other_value, (int, float)):
                if not value == pytest.approx(other_value, rel=rel, abs=abs):
                    return False
            elif isinstance(value, list) and isinstance(other_value, list):
                if not value == pytest.approx(other_value, rel=rel, abs=abs):
                    return False
            else:
                # Incompatible types
                return False
        return True
