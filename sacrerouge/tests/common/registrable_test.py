import unittest

from sacrerouge.common import Registrable


class TestRegistrable(unittest.TestCase):
    class _Base1(Registrable):
        pass

    @_Base1.register('subclass1')
    class _Subclass1(_Base1):
        pass

    class _Base2(Registrable):
        pass

    @_Base2.register('subclass2')
    class _Subclass2(_Base2):
        pass

    def test_register(self):
        assert Registrable._registry == {
            TestRegistrable._Base1: {'subclass1': (TestRegistrable._Subclass1, None)},
            TestRegistrable._Base2: {'subclass2': (TestRegistrable._Subclass2, None)}
        }