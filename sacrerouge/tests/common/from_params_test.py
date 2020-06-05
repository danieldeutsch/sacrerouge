import unittest

from sacrerouge.common import FromParams, Params, Registrable


class TestFromParams(unittest.TestCase):
    class _Base1(Registrable):
        pass

    @_Base1.register('subclass1')
    class _Subclass1(_Base1):
        def __init__(self, a: int, b: str):
            self.a = a
            self.b = b

    def test_from_params(self):
        params = Params({
            'type': 'subclass1',
            'a': 4,
            'b': 'abc'
        })
        obj = TestFromParams._Base1.from_params(params)
        target = TestFromParams._Subclass1(4, 'abc')

        assert isinstance(obj, TestFromParams._Subclass1)
        assert obj.a == target.a
        assert obj.b == target.b