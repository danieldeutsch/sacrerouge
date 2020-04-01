from overrides import overrides
from typing import Any, Dict, List


class Jackknifer(object):
    def get_jackknifing_fields_list(self, fields: Dict[str, Any]) -> List[Dict[str, Any]]:
        raise NotImplementedError


class ReferencesJackknifer(Jackknifer):
    @overrides
    def get_jackknifing_fields_list(self, fields: Dict[str, Any]) -> List[Dict[str, Any]]:
        references = fields['references']
        if len(references) == 1:
            # No jackknifing can be done, return `None` to indicate it cannot be done
            return None

        jk_fields_list = []
        for i in range(len(references)):
            # Copy the original fields and replace the references
            jk_fields = dict(fields)
            jk_fields['references'] = references[:i] + references[i + 1:]
            jk_fields_list.append(jk_fields)
        return jk_fields_list
