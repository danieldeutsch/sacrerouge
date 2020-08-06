import os
import pytest

from sacrerouge.common.testing.metric_test_cases import ReferenceBasedMetricTestCase
from sacrerouge.data import MetricsDict, Pyramid, PyramidAnnotation
from sacrerouge.io import JsonlReader
from sacrerouge.metrics import PyramidScore

_pyramid_file_path = 'datasets/duc-tac/tac2008/v1.0/task1.A.pyramids.jsonl'
_annotation_file_path = 'datasets/duc-tac/tac2008/v1.0/task1.A.pyramid-annotations.jsonl'


class TestPyramidScore(ReferenceBasedMetricTestCase):
    @pytest.mark.skipif(not os.path.exists(_pyramid_file_path), reason='TAC 2008 pyramids file does not exist')
    @pytest.mark.skipif(not os.path.exists(_annotation_file_path), reason='TAC 2008 pyramid annotations file does not exist')
    def test_pyramid_score(self):
        # This is a regression test, not necessarily a test for correctness
        pyramids = {pyramid.instance_id: pyramid for pyramid in JsonlReader(_pyramid_file_path, Pyramid).read()}
        annotations = JsonlReader(_annotation_file_path, PyramidAnnotation).read()
        annotation_pyramids = [pyramids[annotation.instance_id] for annotation in annotations]

        metric = PyramidScore()
        actual_output = metric.score_all(annotations, annotation_pyramids)[:5]
        expected_output = [
            {'modified_pyramid_score': 0.2413793103448276},
            {'modified_pyramid_score': 0.0},
            {'modified_pyramid_score': 0.06896551724137931},
            {'modified_pyramid_score': 0.034482758620689655},
            {'modified_pyramid_score': 0.1724137931034483}
        ]
        for i, (expected, actual) in enumerate(zip(expected_output, actual_output)):
            assert actual.approx_equal(MetricsDict(expected), abs=1e-4), f'Instance {i} not equal. Expected {expected}, actual {actual}'
