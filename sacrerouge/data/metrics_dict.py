import copy
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


def main():
    import jsons

    d = MetricsDict()
    d['a']['b']['c'] = 5

    e = MetricsDict()
    e['a']['b']['c'] = 2

    f = MetricsDict()
    f['a']['b']['c'] = 1

    f = MetricsDict()
    f['a']['b']['c'] = [1, 5]

    g = jsons.loads(jsons.dumps(f), MetricsDict)


if __name__ == '__main__':
    main()
