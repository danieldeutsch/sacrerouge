from typing import List

from sacrerouge.data import EvalInstance
from sacrerouge.data.dataset_readers import DatasetReader
from sacrerouge.data.fields import Fields, SummaryField
from sacrerouge.io import JsonlReader


@DatasetReader.register('summary-only')
class SummaryOnlyDatasetReader(DatasetReader):
    def read(self, input_jsonl: str) -> List[EvalInstance]:
        instances = []
        with JsonlReader(input_jsonl) as f:
            for data in f:
                summary = SummaryField(data['summary']['text'])
                fields = Fields({})

                instance = EvalInstance(
                    data['instance_id'],
                    data['summarizer_id'],
                    data['summarizer_type'],
                    summary,
                    fields
                )
                instances.append(instance)
            return instances
