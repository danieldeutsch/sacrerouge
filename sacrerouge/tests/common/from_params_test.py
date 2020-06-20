import unittest
from typing import Dict, List

from sacrerouge.common import FromParams, Params, Registrable


class _Base1(Registrable):
    pass


@_Base1.register('subclass1')
class _Subclass1(_Base1):
    def __init__(self, a: int, b: str):
        self.a = a
        self.b = b


@_Base1.register('subclass2')
class _Subclass2(_Base1):
    def __init__(self,
                 first: List[_Base1],
                 second: Dict[str, _Base1]):
        self.first = first
        self.second = second


class TestFromParams(unittest.TestCase):
    def test_from_params(self):
        params = Params({
            'type': 'subclass1',
            'a': 4,
            'b': 'abc'
        })
        obj = _Base1.from_params(params)
        target = _Subclass1(4, 'abc')

        assert isinstance(obj, _Subclass1)
        assert obj.a == target.a
        assert obj.b == target.b

    def test_from_params_complex_types(self):
        params = Params({
            'type': 'subclass2',
            'first': [
                {'type': 'subclass1', 'a': 4, 'b': 'abc'},
                {'type': 'subclass1', 'a': 8, 'b': 'def'},
            ],
            'second': {
                'A': {'type': 'subclass1', 'a': 7, 'b': 'ghi'},
                'B': {'type': 'subclass1', 'a': 3, 'b': 'jkl'},
            }
        })
        obj = _Base1.from_params(params)
        target = _Subclass2(
            [
                _Subclass1(4, 'abc'),
                _Subclass1(8, 'def')
            ],
            {
                'A': _Subclass1(7, 'ghi'),
                'B': _Subclass1(3, 'jkl')
            }
        )

        assert isinstance(obj, _Subclass2)
        assert len(obj.first) == 2
        assert obj.first[0].a == 4
        assert obj.first[0].b == 'abc'
        assert obj.first[1].a == 8
        assert obj.first[1].b == 'def'

        assert len(obj.second) == 2
        assert obj.second['A'].a == 7
        assert obj.second['A'].b == 'ghi'
        assert obj.second['B'].a == 3
        assert obj.second['B'].b == 'jkl'
