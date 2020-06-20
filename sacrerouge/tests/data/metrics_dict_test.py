import unittest

from sacrerouge.data import MetricsDict


class TestMetricsDict(unittest.TestCase):
    def test_get_set_item(self):
        metrics = MetricsDict()

        metrics['a'] = 4
        assert metrics['a'] == 4

        metrics['b']['c'] = [1, 2]
        assert metrics['b']['c'] == [1, 2]
        assert isinstance(metrics['b'], MetricsDict)

        metrics['d'] = {'e': 4, 'f': {'g': 4}}
        assert metrics['d'] == {'e': 4, 'f': {'g': 4}}
        assert isinstance(metrics['d'], MetricsDict)
        assert isinstance(metrics['d']['f'], MetricsDict)

    def test_add(self):
        a = MetricsDict({'k1': 1, 'k2': {'k3': 4}})
        b = MetricsDict({'k1': 2, 'k2': {'k3': 5}})
        c = MetricsDict({'k1': 3, 'k2': {'k3': 6}})

        assert a + b == {'k1': 3, 'k2': {'k3': 9}}
        assert a == {'k1': 1, 'k2': {'k3': 4}}
        assert b == {'k1': 2, 'k2': {'k3': 5}}

        assert sum([a, b, c]) == {'k1': 6, 'k2': {'k3': 15}}
        assert a == {'k1': 1, 'k2': {'k3': 4}}
        assert b == {'k1': 2, 'k2': {'k3': 5}}
        assert c == {'k1': 3, 'k2': {'k3': 6}}

    def test_divide(self):
        metrics = MetricsDict({'k1': 1, 'k2': {'k3': 4}})
        assert metrics / 2 == {'k1': 0.5, 'k2': {'k3': 2.0}}
        assert metrics == {'k1': 1, 'k2': {'k3': 4}}

    def test_average_values(self):
        metrics = MetricsDict({'k1': 1, 'k2': {'k3': [1, 2, 3]}})
        assert metrics.average_values() == {'k1': 1, 'k2': {'k3': 2.0}}
        assert metrics == {'k1': 1, 'k2': {'k3': [1, 2, 3]}}

    def test_flatten_keys(self):
        metrics = MetricsDict({'k1': 1, 'k2': {'k3': 4}})
        assert metrics.flatten_keys() == {'k1': 1, 'k2_k3': 4}
        assert metrics == {'k1': 1, 'k2': {'k3': 4}}

    def test_init_with_metrics_dict(self):
        a = MetricsDict({'k1': 1, 'k2': {'k3': [1, 2, 3]}})
        b = MetricsDict(a)

        b['k2']['k3'].append(4)
        assert a == {'k1': 1, 'k2': {'k3': [1, 2, 3]}}
        assert b == {'k1': 1, 'k2': {'k3': [1, 2, 3, 4]}}

    def test_update(self):
        m1 = MetricsDict({'k1': 1, 'k2': {'k3': [1, 2, 3]}})
        m2 = MetricsDict({'k4': 4, 'k2': {'k3': 5, 'k5': 8}})
        m1.update(m2)
        assert m1 == {'k1': 1, 'k2': {'k3': 5, 'k5': 8}, 'k4': 4}

    def test_approx_equal(self):
        m1 = MetricsDict({'k1': 1, 'k2': {'k3': [1, 2, 3]}})
        m2 = MetricsDict({'k1': 1.01, 'k2': {'k3': [1.01, 2.01, 3.01]}})
        assert m1.approx_equal(m2, abs=0.02)

        # Wrong keys
        m1 = MetricsDict({'k1': 1})
        m2 = MetricsDict({'k2': 1})
        assert not m1.approx_equal(m2, abs=0.02)

        # Wrong types
        m1 = MetricsDict({'k1': 1, 'k2': {'k3': 1.0}})
        m2 = MetricsDict({'k1': 1.01, 'k2': {'k3': [1.01, 2.01, 3.01]}})
        assert not m1.approx_equal(m2, abs=0.02)

        # Too different
        m1 = MetricsDict({'k1': 1})
        m2 = MetricsDict({'k1': 1.5})
        assert not m1.approx_equal(m2, abs=0.02)

