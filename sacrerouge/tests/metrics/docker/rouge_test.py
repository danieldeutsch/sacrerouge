import pytest
from repro.common.docker import image_exists

from sacrerouge.common.testing.metric_test_cases import ReferenceBasedMetricTestCase
from sacrerouge.common.testing.util import sacrerouge_command_exists
from sacrerouge.metrics.docker import DockerRouge


@pytest.mark.skipif(not image_exists("lin2004"), reason="Docker image \"lin2004\" does not exist")
class TestROUGE(ReferenceBasedMetricTestCase):
    def test_rouge(self):
        # This is a regression test, not necessarily a test for correctness
        metric = DockerRouge()
        expected_output = [
            {
                "rouge-1": {
                    "recall": 40.516000000000005,
                    "precision": 41.699999999999996,
                    "f1": 41.099000000000004
                },
                "rouge-2": {
                    "recall": 10.233,
                    "precision": 10.533,
                    "f1": 10.381
                },
                "rouge-3": {
                    "recall": 4.2909999999999995,
                    "precision": 4.417999999999999,
                    "f1": 4.354
                },
                "rouge-4": {
                    "recall": 3.1329999999999996,
                    "precision": 3.2259999999999995,
                    "f1": 3.179
                },
                "rouge-l": {
                    "recall": 36.258,
                    "precision": 37.317,
                    "f1": 36.78
                },
                "rouge-su4": {
                    "recall": 15.732,
                    "precision": 16.197,
                    "f1": 15.961
                }
            },
            {
                "rouge-1": {
                    "recall": 48.258,
                    "precision": 47.765,
                    "f1": 48.010000000000005
                },
                "rouge-2": {
                    "recall": 19.301,
                    "precision": 19.103,
                    "f1": 19.200999999999997
                },
                "rouge-3": {
                    "recall": 10.403,
                    "precision": 10.296,
                    "f1": 10.349
                },
                "rouge-4": {
                    "recall": 6.9190000000000005,
                    "precision": 6.848,
                    "f1": 6.883
                },
                "rouge-l": {
                    "recall": 44.774,
                    "precision": 44.317,
                    "f1": 44.544
                },
                "rouge-su4": {
                    "recall": 21.751,
                    "precision": 21.526999999999997,
                    "f1": 21.637999999999998
                }
            },
            {
                "rouge-1": {
                    "recall": 49.416,
                    "precision": 48.659,
                    "f1": 49.035000000000004
                },
                "rouge-2": {
                    "recall": 16.406000000000002,
                    "precision": 16.154,
                    "f1": 16.279
                },
                "rouge-3": {
                    "recall": 8.235000000000001,
                    "precision": 8.108,
                    "f1": 8.171000000000001
                },
                "rouge-4": {
                    "recall": 5.118,
                    "precision": 5.039,
                    "f1": 5.078
                },
                "rouge-l": {
                    "recall": 45.72,
                    "precision": 45.019,
                    "f1": 45.367000000000004
                },
                "rouge-su4": {
                    "recall": 19.954,
                    "precision": 19.645000000000003,
                    "f1": 19.798
                }
            },
            {
                "rouge-1": {
                    "recall": 44.466,
                    "precision": 44.038,
                    "f1": 44.251000000000005
                },
                "rouge-2": {
                    "recall": 11.891,
                    "precision": 11.776,
                    "f1": 11.833
                },
                "rouge-3": {
                    "recall": 3.914,
                    "precision": 3.8760000000000003,
                    "f1": 3.895
                },
                "rouge-4": {
                    "recall": 1.7680000000000002,
                    "precision": 1.7510000000000001,
                    "f1": 1.7590000000000001
                },
                "rouge-l": {
                    "recall": 40.971000000000004,
                    "precision": 40.577000000000005,
                    "f1": 40.772999999999996
                },
                "rouge-su4": {
                    "recall": 16.154,
                    "precision": 15.997,
                    "f1": 16.075
                }
            },
            {
                "rouge-1": {
                    "recall": 42.403999999999996,
                    "precision": 41.473,
                    "f1": 41.933
                },
                "rouge-2": {
                    "recall": 10.477,
                    "precision": 10.245999999999999,
                    "f1": 10.36
                },
                "rouge-3": {
                    "recall": 4.128,
                    "precision": 4.036,
                    "f1": 4.0809999999999995
                },
                "rouge-4": {
                    "recall": 1.6039999999999999,
                    "precision": 1.569,
                    "f1": 1.5859999999999999
                },
                "rouge-l": {
                    "recall": 37.649,
                    "precision": 36.822,
                    "f1": 37.230999999999995
                },
                "rouge-su4": {
                    "recall": 16.311,
                    "precision": 15.949,
                    "f1": 16.128
                }
            },
            {
                "rouge-1": {
                    "recall": 43.857,
                    "precision": 43.061,
                    "f1": 43.455
                },
                "rouge-2": {
                    "recall": 13.395000000000001,
                    "precision": 13.150999999999998,
                    "f1": 13.272
                },
                "rouge-3": {
                    "recall": 4.261,
                    "precision": 4.183,
                    "f1": 4.222
                },
                "rouge-4": {
                    "recall": 1.471,
                    "precision": 1.444,
                    "f1": 1.4569999999999999
                },
                "rouge-l": {
                    "recall": 40.555,
                    "precision": 39.818,
                    "f1": 40.183
                },
                "rouge-su4": {
                    "recall": 18.247,
                    "precision": 17.912,
                    "f1": 18.078
                }
            },
            {
                "rouge-1": {
                    "recall": 52.39,
                    "precision": 51.568999999999996,
                    "f1": 51.976
                },
                "rouge-2": {
                    "recall": 20.4,
                    "precision": 20.079,
                    "f1": 20.238
                },
                "rouge-3": {
                    "recall": 8.434,
                    "precision": 8.3,
                    "f1": 8.366
                },
                "rouge-4": {
                    "recall": 4.234,
                    "precision": 4.167,
                    "f1": 4.2
                },
                "rouge-l": {
                    "recall": 47.211,
                    "precision": 46.471000000000004,
                    "f1": 46.838
                },
                "rouge-su4": {
                    "recall": 23.557,
                    "precision": 23.183999999999997,
                    "f1": 23.369
                }
            },
            {
                "rouge-1": {
                    "recall": 51.186,
                    "precision": 51.593999999999994,
                    "f1": 51.388999999999996
                },
                "rouge-2": {
                    "recall": 20.238,
                    "precision": 20.4,
                    "f1": 20.319000000000003
                },
                "rouge-3": {
                    "recall": 7.968,
                    "precision": 8.032,
                    "f1": 8.0
                },
                "rouge-4": {
                    "recall": 3.5999999999999996,
                    "precision": 3.6290000000000004,
                    "f1": 3.614
                },
                "rouge-l": {
                    "recall": 46.64,
                    "precision": 47.012,
                    "f1": 46.825
                },
                "rouge-su4": {
                    "recall": 23.569000000000003,
                    "precision": 23.758000000000003,
                    "f1": 23.663
                }
            },
            {
                "rouge-1": {
                    "recall": 38.635999999999996,
                    "precision": 52.641000000000005,
                    "f1": 44.564
                },
                "rouge-2": {
                    "recall": 13.691,
                    "precision": 18.681,
                    "f1": 15.801000000000002
                },
                "rouge-3": {
                    "recall": 6.468999999999999,
                    "precision": 8.84,
                    "f1": 7.471
                },
                "rouge-4": {
                    "recall": 4.465,
                    "precision": 6.111,
                    "f1": 5.16
                },
                "rouge-l": {
                    "recall": 35.829,
                    "precision": 48.815999999999995,
                    "f1": 41.326
                },
                "rouge-su4": {
                    "recall": 16.689,
                    "precision": 22.828,
                    "f1": 19.282
                }
            },
            {
                "rouge-1": {
                    "recall": 51.73799999999999,
                    "precision": 51.6,
                    "f1": 51.669
                },
                "rouge-2": {
                    "recall": 23.49,
                    "precision": 23.427,
                    "f1": 23.458000000000002
                },
                "rouge-3": {
                    "recall": 11.59,
                    "precision": 11.559,
                    "f1": 11.574
                },
                "rouge-4": {
                    "recall": 7.983999999999999,
                    "precision": 7.962,
                    "f1": 7.973
                },
                "rouge-l": {
                    "recall": 49.332,
                    "precision": 49.2,
                    "f1": 49.266
                },
                "rouge-su4": {
                    "recall": 25.202999999999996,
                    "precision": 25.135,
                    "f1": 25.169000000000004
                }
            },
            {
                "rouge-1": {
                    "recall": 48.79,
                    "precision": 48.016,
                    "f1": 48.4
                },
                "rouge-2": {
                    "recall": 21.053,
                    "precision": 20.717,
                    "f1": 20.884
                },
                "rouge-3": {
                    "recall": 11.584999999999999,
                    "precision": 11.4,
                    "f1": 11.491999999999999
                },
                "rouge-4": {
                    "recall": 7.550999999999999,
                    "precision": 7.430000000000001,
                    "f1": 7.489999999999999
                },
                "rouge-l": {
                    "recall": 47.782000000000004,
                    "precision": 47.024,
                    "f1": 47.4
                },
                "rouge-su4": {
                    "recall": 23.607,
                    "precision": 23.229,
                    "f1": 23.416
                }
            },
            {
                "rouge-1": {
                    "recall": 44.711,
                    "precision": 45.344,
                    "f1": 45.025
                },
                "rouge-2": {
                    "recall": 15.03,
                    "precision": 15.244,
                    "f1": 15.136
                },
                "rouge-3": {
                    "recall": 6.841,
                    "precision": 6.938999999999999,
                    "f1": 6.890000000000001
                },
                "rouge-4": {
                    "recall": 4.04,
                    "precision": 4.098,
                    "f1": 4.069
                },
                "rouge-l": {
                    "recall": 44.112,
                    "precision": 44.737,
                    "f1": 44.422
                },
                "rouge-su4": {
                    "recall": 19.2,
                    "precision": 19.475,
                    "f1": 19.337
                }
            }
        ]
        super().assert_expected_output(metric, expected_output)

    def test_rouge_order_invariant(self):
        metric = DockerRouge()
        self.assert_order_invariant(metric)

    def test_command_exists(self):
        assert sacrerouge_command_exists(['docker-rouge'])
