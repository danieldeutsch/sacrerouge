from collections import defaultdict
from typing import Dict, Type

from sacrerouge.common import FromParams


class Registrable(FromParams):
    _registry: Dict[Type, Dict[str, Type]] = defaultdict(dict)

    @classmethod
    def register(cls: Type, name: str):
        def _register(subclass: Type):
            Registrable._registry[cls][name] = subclass
            return subclass
        return _register
