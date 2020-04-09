from typing import Type

from sacrerouge.common import Params


class FromParams(object):
    @classmethod
    def from_params(cls: Type, params: Params) -> 'FromParams':
        type_ = params.pop('type')
        cls_ = cls._registry[type_]
        return cls_(**params)
