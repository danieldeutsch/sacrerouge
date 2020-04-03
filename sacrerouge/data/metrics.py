import jsons
from collections import OrderedDict
from jsons import JsonSerializable
from typing import Dict, Optional, Union

from sacrerouge.data.metrics_dict import MetricsDict


class Metrics(object):
    def __init__(self,
                 instance_id: str,
                 summarizer_id: str,
                 summarizer_type: str,
                 metrics: Optional[Union[MetricsDict, Dict]] = None) -> None:
        self.instance_id = instance_id
        self.summarizer_id = summarizer_id
        self.summarizer_type = summarizer_type
        self.metrics = MetricsDict(metrics) if metrics else MetricsDict()

    def flatten_keys(self) -> None:
        self.metrics = self.metrics.flatten_keys()

    def average_values(self) -> None:
        self.metrics = self.metrics.average_values()

    def merge(self, other: 'Metrics') -> None:
        if self.instance_id != other.instance_id or \
                self.summarizer_id != other.summarizer_id or \
                self.summarizer_type != other.summarizer_type:
            raise Exception(f'Cannot merge two Metrics if metadata is not the same.')

        for key, value in other.metrics.items():
            self.metrics[key] = value

    def __eq__(self, other: 'Metrics') -> bool:
        if self.instance_id != other.instance_id or \
                self.summarizer_id != other.summarizer_id or \
                self.summarizer_type != other.summarizer_type:
            return False
        return self.metrics == other.metrics

    def __repr__(self) -> str:
        return jsons.dumps(Metrics.serialize(self))

    @staticmethod
    def serialize(metrics: 'Metrics', **kwargs) -> OrderedDict:
        # I think controlling the order of the keys in the serialization
        # aids readability when the json is deserialized. The jsons library
        # will sort the keys if we don't do this
        return OrderedDict({
            'instance_id': metrics.instance_id,
            'summarizer_id': metrics.summarizer_id,
            'summarizer_type': metrics.summarizer_type,
            'metrics': metrics.metrics
        })


JsonSerializable.set_serializer(Metrics.serialize, Metrics)
