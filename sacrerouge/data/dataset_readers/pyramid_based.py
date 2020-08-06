import logging
from typing import List

from sacrerouge.data import EvalInstance, Pyramid, PyramidAnnotation
from sacrerouge.data.dataset_readers import DatasetReader
from sacrerouge.data.fields import Fields, PyramidField, PyramidAnnotationField, ReferencesField, SummaryField
from sacrerouge.io import JsonlReader

logger = logging.getLogger(__name__)


@DatasetReader.register('pyramid-based')
class ReferenceBasedDatasetReader(DatasetReader):
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
        with JsonlReader(annotation_jsonl, PyramidAnnotation) as f:
            for annotation in f:
                fields = Fields({
                    'annotation': PyramidAnnotationField(annotation),
                    'pyramid': PyramidField(pyramids[annotation.pyramid.instance_id])
                })

                instance = EvalInstance(
                    annotation.instance_id,
                    annotation.summarizer_id,
                    annotation.summarizer_type,
                    fields
                )
                instances.append(instance)

            logger.info(f'Loaded {len(instances)} Pyramid annotations')
            return instances
