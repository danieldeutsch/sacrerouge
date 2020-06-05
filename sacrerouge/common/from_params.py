from typing import Type

from sacrerouge.common import Params


class FromParams(object):
    @classmethod
    def from_params(cls: Type, params: Params) -> 'FromParams':
        from sacrerouge.common.registrable import Registrable  # import here to avoid circular imports
        type_ = params.pop('type')
        cls_ = Registrable._registry[cls][type_]
        return cls_(**params)
