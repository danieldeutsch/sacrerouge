import os
import pytest
import unittest
from collections import defaultdict

from sacrerouge.data import Pyramid, PyramidAnnotation
from sacrerouge.io import JsonlReader


_pyramids_task1_file_path = 'datasets/duc-tac/duc2007/v1.0/task1.pyramids.jsonl'
_pyramids_task2_file_path = 'datasets/duc-tac/duc2007/v1.0/task2.A-B-C.pyramids.jsonl'
_pyramid_task1_annotations_file_path = 'datasets/duc-tac/duc2007/v1.0/task1.pyramid-annotations.jsonl'
_pyramid_task2_annotations_file_path = 'datasets/duc-tac/duc2007/v1.0/task2.A-B-C.pyramid-annotations.jsonl'


@pytest.mark.skipif(not os.path.exists(_pyramids_task1_file_path), reason='DUC 2007 Pyramids file does not exist')
@pytest.mark.skipif(not os.path.exists(_pyramids_task2_file_path), reason='DUC 2007 Pyramids file does not exist')
@pytest.mark.skipif(not os.path.exists(_pyramid_task1_annotations_file_path), reason='DUC 2007 Pyramid annotations file does not exist')
@pytest.mark.skipif(not os.path.exists(_pyramid_task2_annotations_file_path), reason='DUC 2007 Pyramid annotations file does not exist')
class TestDUC2007Pyramids(unittest.TestCase):
    def test_pyramids_task1(self):
        """Do some basic sanity tests on the files."""
        pyramids = JsonlReader(_pyramids_task1_file_path, Pyramid).read()
        annotations = JsonlReader(_pyramid_task1_annotations_file_path, PyramidAnnotation).read()

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

    def test_pyramids_task2(self):
        """Do some basic sanity tests on the files."""
        pyramids = JsonlReader(_pyramids_task2_file_path, Pyramid).read()
        annotations = JsonlReader(_pyramid_task2_annotations_file_path, PyramidAnnotation).read()

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

    def test_pyramid_examples_task1(self):
        """Pick some random examples and test them."""
        pyramids = JsonlReader(_pyramids_task1_file_path, Pyramid).read()
        annotations = JsonlReader(_pyramid_task1_annotations_file_path, PyramidAnnotation).read()

        instance_id_to_pyramid = {}
        for pyramid in pyramids:
            instance_id_to_pyramid[pyramid.instance_id] = pyramid

        instance_id_to_annotations = defaultdict(dict)
        for annotation in annotations:
            instance_id_to_annotations[annotation.instance_id][annotation.summarizer_id] = annotation

        pyramid = instance_id_to_pyramid['d0701']
        assert pyramid.summarizer_ids == ['A', 'G', 'H', 'I']
        annotation = instance_id_to_annotations['d0701']['2']
        label = 'Southern Poverty Law Center, a civil rights organization in Montgomery, Ala'
        assert len(annotation.scus) == 5
        assert annotation.scus[2].scu_id == 9
        assert len(annotation.scus[2].contributors) == 1
        assert annotation.scus[2].contributors[0].label == label
        assert len(annotation.scus[2].contributors[0].parts) == 1
        assert annotation.scus[2].contributors[0].parts[0].text == label
        start = annotation.scus[2].contributors[0].parts[0].start
        end = annotation.scus[2].contributors[0].parts[0].end
        assert annotation.summary[start:end] == label
        self._test_example(pyramid, annotation)

        pyramid = instance_id_to_pyramid['d0706']
        assert pyramid.summarizer_ids == ['B', 'D', 'E', 'I']
        annotation = instance_id_to_annotations['d0706']['14']
        label = 'SLORC - State Law and Order Restoration Council - which took over Burma in 1988'
        assert len(annotation.scus) == 3  # There are 4 in the file but SCU 10 has errors in the Pyramid, so it is skipped
        assert annotation.scus[0].scu_id == 37
        assert len(annotation.scus[0].contributors) == 1
        assert annotation.scus[0].contributors[0].label == label
        assert len(annotation.scus[0].contributors[0].parts) == 1
        assert annotation.scus[0].contributors[0].parts[0].text == label
        start = annotation.scus[0].contributors[0].parts[0].start
        end = annotation.scus[0].contributors[0].parts[0].end
        assert annotation.summary[start:end] == label
        self._test_example(pyramid, annotation)

    def test_pyramid_examples_task2(self):
        """Pick some random examples and test them."""
        pyramids = JsonlReader(_pyramids_task2_file_path, Pyramid).read()
        annotations = JsonlReader(_pyramid_task2_annotations_file_path, PyramidAnnotation).read()

        instance_id_to_pyramid = {}
        for pyramid in pyramids:
            instance_id_to_pyramid[pyramid.instance_id] = pyramid

        instance_id_to_annotations = defaultdict(dict)
        for annotation in annotations:
            instance_id_to_annotations[annotation.instance_id][annotation.summarizer_id] = annotation

        pyramid = instance_id_to_pyramid['d0716-B']
        assert pyramid.summarizer_ids == ['C', 'D', 'E', 'F']
        annotation = instance_id_to_annotations['d0716-B']['49']
        contrib_label = 'U.N. team...is investigating whether the mine threatens the environmental and cultural values of Kakadu'
        part_label = 'U.N. team'
        assert len(annotation.scus) == 1
        assert annotation.scus[0].scu_id == 6
        assert len(annotation.scus[0].contributors) == 1
        assert annotation.scus[0].contributors[0].label == contrib_label
        assert len(annotation.scus[0].contributors[0].parts) == 2
        assert annotation.scus[0].contributors[0].parts[0].text == part_label
        start = annotation.scus[0].contributors[0].parts[0].start
        end = annotation.scus[0].contributors[0].parts[0].end
        assert annotation.summary[start:end] == part_label
        self._test_example(pyramid, annotation)

        pyramid = instance_id_to_pyramid['d0727-C']
        assert pyramid.summarizer_ids == ['A', 'F', 'G', 'H']
        annotation = instance_id_to_annotations['d0727-C']['40']
        label = "Newt Gingrich and the former aide with whom he acknowledged an ''intimate relationship''"
        assert len(annotation.scus) == 3
        assert annotation.scus[2].scu_id == 32
        assert len(annotation.scus[2].contributors) == 1
        assert annotation.scus[2].contributors[0].label == label
        assert len(annotation.scus[2].contributors[0].parts) == 1
        assert annotation.scus[2].contributors[0].parts[0].text == label
        start = annotation.scus[2].contributors[0].parts[0].start
        end = annotation.scus[2].contributors[0].parts[0].end
        assert annotation.summary[start:end] == label
        self._test_example(pyramid, annotation)
