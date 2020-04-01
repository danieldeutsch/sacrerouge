from typing import Any, Dict, List, Type

from sacrerouge.data import EvalInstance


class DatasetReader(object):
    _registry: Dict[str, Type] = {}

    def read(self) -> List[EvalInstance]:
        raise NotImplementedError

    @classmethod
    def register(cls: Type, name: str):
        def _register(subclass: Type):
            cls._registry[name] = subclass
            return subclass
        return _register

    @classmethod
    def from_params(cls: Type, params: Dict[str, Any]) -> 'DatasetReader':
        reader_type = params.pop('type')
        reader_cls = cls._registry[reader_type]
        return reader_cls(**params)
