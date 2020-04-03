from overrides import overrides
from typing import List

from sacrerouge.data.fields import Fields, ReferencesField


class Jackknifer(object):
    def get_jackknifing_fields_list(self, fields: Fields) -> List[Fields]:
        raise NotImplementedError


class ReferencesJackknifer(Jackknifer):
    @overrides
    def get_jackknifing_fields_list(self, fields: Fields) -> List[Fields]:
        references_field = fields['references']
        if len(references_field.references) == 1:
            # No jackknifing can be done, return `None` to indicate it cannot be done
            return None

        jk_fields_list = []
        for i in range(len(references_field.references)):
            # Copy the original fields and replace the references
            jk_fields = Fields(fields)
            jk_fields['references'] = ReferencesField(references_field.references[:i] + references_field.references[i + 1:])
            jk_fields_list.append(jk_fields)
        return jk_fields_list
