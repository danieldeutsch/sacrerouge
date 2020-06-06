import os
import pytest
import unittest
from collections import defaultdict

from sacrerouge.data import Pyramid, PyramidAnnotation
from sacrerouge.io import JsonlReader


_pyramids_file_path = 'datasets/duc-tac/tac2011/v1.0/task1.A-B.pyramids.jsonl'
_pyramid_annotations_file_path = 'datasets/duc-tac/tac2011/v1.0/task1.A-B.pyramid-annotations.jsonl'


@pytest.mark.skipif(not os.path.exists(_pyramids_file_path), reason='TAC 2011 Pyramids file does not exist')
@pytest.mark.skipif(not os.path.exists(_pyramid_annotations_file_path), reason='TAC 2011 Pyramid annotations file does not exist')
class TestTAC2011Pyramids(unittest.TestCase):
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
            # For some reason, this one pyramid has 8 summaries
            if instance_id in ['d1129-B']:
                assert len(pyramid.summaries) == 8, (instance_id,)
                assert len(pyramid.summarizer_ids) == 8
            else:
                assert len(pyramid.summaries) == 4, (instance_id,)
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

        pyramid = instance_id_to_pyramid['d1101-A']
        assert pyramid.summarizer_ids == ['A', 'B', 'C', 'D']
        annotation = instance_id_to_annotations['d1101-A']['1']
        label = 'Roberts entered the school'
        contrib_label = 'gunman inside their tiny one-room schoolhouse'
        assert len(annotation.scus) == 2
        assert annotation.scus[0].scu_id == 2
        assert len(annotation.scus[0].contributors) == 1
        assert annotation.scus[0].contributors[0].label == contrib_label
        assert len(annotation.scus[0].contributors[0].parts) == 1
        assert annotation.scus[0].contributors[0].parts[0].text == contrib_label
        start = annotation.scus[0].contributors[0].parts[0].start
        end = annotation.scus[0].contributors[0].parts[0].end
        assert annotation.summary[start:end] == contrib_label
        self._test_example(pyramid, annotation)

        # This is an example of a pyramid annotation that has SCUs that are
        # not present in the pyramid, therefore they are missing here.
        pyramid = instance_id_to_pyramid['d1112-B']
        assert pyramid.summarizer_ids == ['A', 'C', 'G', 'H']
        annotation = instance_id_to_annotations['d1112-B']['22']
        contrib_label = 'some jurors in the Metrolink train derailment case last month said they really didn\'t think Alvarez intended to kill anyone'
        part_label = 'some jurors in the Metrolink train derailment case last month said they really didn\'t think Alvarez intended to kill anyone'
        assert len(annotation.scus) == 1
        assert annotation.scus[0].scu_id == 41
        assert len(annotation.scus[0].contributors) == 1
        assert annotation.scus[0].contributors[0].label == contrib_label
        assert len(annotation.scus[0].contributors[0].parts) == 1
        assert annotation.scus[0].contributors[0].parts[0].text == part_label
        start = annotation.scus[0].contributors[0].parts[0].start
        end = annotation.scus[0].contributors[0].parts[0].end
        assert annotation.summary[start:end] == part_label
        # This annotation has an incorrect SCU ID. It should be 7 but it is 41,
        # so we cannot call the next method or it will fail.
        # self._test_example(pyramid, annotation)
