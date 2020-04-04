from typing import Any, Dict, Type


class FromParams(object):
    @classmethod
    def from_params(cls: Type, params: Dict[str, Any]) -> 'FromParams':
        metric_type = params.pop('type')
        metric_cls = cls._registry[metric_type]
        return metric_cls(**params)
