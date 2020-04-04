import os
import pytest
import unittest
from collections import defaultdict

from sacrerouge.data import Pyramid, PyramidAnnotation
from sacrerouge.io import JsonlReader


_pyramids_file_path = 'datasets/duc-tac/tac2010/v1.0/task1.A-B.pyramids.jsonl'
_pyramid_annotations_file_path = 'datasets/duc-tac/tac2010/v1.0/task1.A-B.pyramid-annotations.jsonl'


@pytest.mark.skipif(not os.path.exists(_pyramids_file_path), reason='TAC 2010 Pyramids file does not exist')
@pytest.mark.skipif(not os.path.exists(_pyramid_annotations_file_path), reason='TAC 2010 Pyramid annotations file does not exist')
class TestTAC2010Pyramids(unittest.TestCase):
    def test_pyramids(self):
        """Do some basic sanity tests on the files."""
        pyramids = JsonlReader(_pyramids_file_path, Pyramid).read()
        annotations = JsonlReader(_pyramid_annotations_file_path, PyramidAnnotation).read()

        instance_id_to_pyramid = {}
        for pyramid in pyramids:
            instance_id_to_pyramid[pyramid.instance_id] = pyramid

        instance_id_to_annotations = defaultdict(list)
        for annotation in annotations:
            instance_id_to_annotations[annotation.instance_id].append(annotation)

        assert instance_id_to_pyramid.keys() == instance_id_to_annotations.keys()
        for instance_id, pyramid in instance_id_to_pyramid.items():
            assert len(pyramid.summaries) == 4
            assert len(pyramid.summarizer_ids) == 4
            for reference in pyramid.summaries:
                assert len(reference) > 0

            scu_ids = set([scu.scu_id for scu in pyramid.scus])
            for annotation in instance_id_to_annotations[instance_id]:
                assert len(annotation.summary) > 0, (instance_id, annotation.summarizer_id)
                for scu in annotation.scus:
                    assert scu.scu_id in scu_ids, (scu.scu_id, scu_ids)

    def _test_example(self, pyramid: Pyramid, annotation: PyramidAnnotation) -> None:
        scu_to_label = {scu.scu_id: scu.label for scu in pyramid.scus}
        for scu in annotation.scus:
            assert scu.label == scu_to_label[scu.scu_id]

    def test_pyramid_examples(self):
        """Pick some random examples and test them."""
        pyramids = JsonlReader(_pyramids_file_path, Pyramid).read()
        annotations = JsonlReader(_pyramid_annotations_file_path, PyramidAnnotation).read()

        instance_id_to_pyramid = {}
        for pyramid in pyramids:
            instance_id_to_pyramid[pyramid.instance_id] = pyramid

        instance_id_to_annotations = defaultdict(dict)
        for annotation in annotations:
            instance_id_to_annotations[annotation.instance_id][annotation.summarizer_id] = annotation

        pyramid = instance_id_to_pyramid['d1001-A']
        assert pyramid.summarizer_ids == ['A', 'B', 'F', 'H']
        annotation = instance_id_to_annotations['d1001-A']['2']
        label = 'Columbine'
        assert len(annotation.scus) == 3
        assert annotation.scus[0].scu_id == 3
        assert len(annotation.scus[0].contributors) == 1
        assert annotation.scus[0].contributors[0].label == label
        assert len(annotation.scus[0].contributors[0].parts) == 1
        assert annotation.scus[0].contributors[0].parts[0].text == label
        start = annotation.scus[0].contributors[0].parts[0].start
        end = annotation.scus[0].contributors[0].parts[0].end
        assert annotation.summary[start:end] == label
        self._test_example(pyramid, annotation)

        pyramid = instance_id_to_pyramid['d1002-A']
        assert pyramid.summarizer_ids == ['A', 'B', 'C', 'D']
        annotation = instance_id_to_annotations['d1002-A']['29']
        contrib_label = 'official investigations _ bythe US Justice Department'
        part_label = 'official investigations _ by the US Justice Department'
        assert len(annotation.scus) == 1
        assert annotation.scus[0].scu_id == 11
        assert len(annotation.scus[0].contributors) == 1
        assert annotation.scus[0].contributors[0].label == contrib_label
        assert len(annotation.scus[0].contributors[0].parts) == 1
        assert annotation.scus[0].contributors[0].parts[0].text == part_label
        start = annotation.scus[0].contributors[0].parts[0].start
        end = annotation.scus[0].contributors[0].parts[0].end
        assert annotation.summary[start:end] == part_label
        self._test_example(pyramid, annotation)
