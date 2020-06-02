from typing import Dict, Type

from sacrerouge.common import FromParams


class Registrable(FromParams):
    _registry: Dict[str, Type] = {}
    _parents: Dict[str, str] = {}

    @classmethod
    def register(cls: Type, name: str, parent: str = None):
        def _register(subclass: Type):
            cls._registry[name] = subclass
            cls._parents[name] = parent
            return subclass
        return _register
