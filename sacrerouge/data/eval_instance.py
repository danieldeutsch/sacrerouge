import jsons

from sacrerouge.data.fields import Fields, SummaryField


class EvalInstance(object):
    def __init__(self,
                 instance_id: str,
                 summarizer_id: str,
                 summarizer_type: str,
                 summary: SummaryField,
                 fields: Fields) -> None:
        self.instance_id = instance_id
        self.summarizer_id = summarizer_id
        self.summarizer_type = summarizer_type
        self.summary = summary
        self.fields = fields

    def __repr__(self) -> str:
        return jsons.dumps(self)
