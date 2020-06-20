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
        assert TestRegistrable._Base1 in Registrable._registry
        assert len(Registrable._registry[TestRegistrable._Base1]) == 1
        assert Registrable._registry[TestRegistrable._Base1]['subclass1'] == (TestRegistrable._Subclass1, None)

        assert TestRegistrable._Base2 in Registrable._registry
        assert len(Registrable._registry[TestRegistrable._Base2]) == 1
        assert Registrable._registry[TestRegistrable._Base2]['subclass2'] == (TestRegistrable._Subclass2, None)
