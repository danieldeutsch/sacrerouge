import logging
from typing import List

from sacrerouge.data import EvalInstance, Pyramid, PyramidAnnotation
from sacrerouge.data.dataset_readers import DatasetReader
from sacrerouge.data.fields import Fields, PyramidField, PyramidAnnotationField, ReferencesField, SummaryField
from sacrerouge.io import JsonlReader

logger = logging.getLogger(__name__)


@DatasetReader.register('pyramid-based')
class PyramidBasedDatasetReader(DatasetReader):
    def __init__(self, include_reference_annotations: bool = True) -> None:
        """
        Args:
            include_reference_annotations: Indicates if pyramid annotations should be created
                for all of the summaries in the pyramid. This will be done for all of the instance_ids
                which are observed in the annotations file.
        """
        super().__init__()
        self.include_reference_annotations = include_reference_annotations

    def read(self,
             pyramid_jsonl: str,
             annotation_jsonl: str) -> List[EvalInstance]:
        logger.info(f'Loading Pyramids from {pyramid_jsonl}')
        pyramids = {}
        with JsonlReader(pyramid_jsonl, Pyramid) as f:
            for pyramid in f:
                pyramids[pyramid.instance_id] = pyramid
        logger.info(f'Loaded {len(pyramids)} pyramids')

        logger.info(f'Loading Pyramid annotations from {annotation_jsonl}')
        instances = []
        instance_ids = set()
        with JsonlReader(annotation_jsonl, PyramidAnnotation) as f:
            for annotation in f:
                fields = Fields({
                    'annotation': PyramidAnnotationField(annotation),
                    'pyramid': PyramidField(pyramids[annotation.instance_id])
                })

                instance = EvalInstance(
                    annotation.instance_id,
                    annotation.summarizer_id,
                    annotation.summarizer_type,
                    fields
                )
                instances.append(instance)

                instance_ids.add(annotation.instance_id)

            logger.info(f'Loaded {len(instances)} Pyramid annotations')

        if self.include_reference_annotations:
            logger.info(f'Generating Pyramid annotations for the reference summaries')
            reference_instances = []
            for instance_id in instance_ids:
                pyramid = pyramids[instance_id]

                # We can only do this if there are > 1 summaries used to construct the pyramid
                if len(pyramid.summarizer_ids) > 1:
                    for i in range(len(pyramid.summarizer_ids)):
                        annotation = pyramid.get_annotation(i)
                        reduced_pyramid = pyramid.remove_summary(i)
                        fields = Fields({
                            'annotation': PyramidAnnotationField(annotation),
                            'pyramid': PyramidField(reduced_pyramid)
                        })
                        instance = EvalInstance(
                            annotation.instance_id,
                            annotation.summarizer_id,
                            annotation.summarizer_type,
                            fields
                        )
                        reference_instances.append(instance)
            logger.info(f'Generated {len(reference_instances)} reference summary annotations')
            instances.extend(reference_instances)

        logger.info(f'Loaded a total of {len(instances)} instances')
        return instances
