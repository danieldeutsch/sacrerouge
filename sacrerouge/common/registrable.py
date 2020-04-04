from typing import Dict, Type

from sacrerouge.common import FromParams


class Registrable(FromParams):
    _registry: Dict[str, Type] = {}

    @classmethod
    def register(cls: Type, name: str):
        def _register(subclass: Type):
            cls._registry[name] = subclass
            return subclass
        return _register
