from typing import Any, Dict

from sacrerouge.data.types import SummaryType


class EvalInstance(object):
    def __init__(self,
                 instance_id: str,
                 summarizer_id: str,
                 summarizer_type: str,
                 summary: SummaryType,
                 fields: Dict[str, Any]) -> None:
        self.instance_id = instance_id
        self.summarizer_id = summarizer_id
        self.summarizer_type = summarizer_type
        self.summary = summary
        self.fields = fields
