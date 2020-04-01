from typing import List

from sacrerouge.data import EvalInstance
from sacrerouge.data.dataset_readers import DatasetReader
from sacrerouge.io import JsonlReader


@DatasetReader.register('reference-based')
class ReferenceBasedDatasetReader(DatasetReader):
    def __init__(self, input_jsonl: str) -> None:
        super().__init__()
        self.input_jsonl = input_jsonl

    def read(self) -> List[EvalInstance]:
        instances = []
        with JsonlReader(self.input_jsonl) as f:
            for data in f:
                summary = data['summary']['text']

                if 'reference' in data:
                    references = [data['reference']['text']]
                else:
                    references = [reference['text'] for reference in data['references']]
                fields = {'references': references}

                instance = EvalInstance(
                    data['instance_id'],
                    data['summarizer_id'],
                    data['summarizer_type'],
                    summary,
                    fields
                )
                instances.append(instance)
            return instances
