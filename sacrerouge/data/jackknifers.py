from overrides import overrides
from typing import List

from sacrerouge.data.fields import Fields, PyramidField, ReferencesField
from sacrerouge.data.pyramid import Pyramid


class Jackknifer(object):
    """
    A `Jackknifer` is responsible for taking a `Fields` object that requires
    jackknifing and converting it to a `List[Fields]` of jackknifed instances such
    that each item in the list is one of the jackknifing evaluations.
    """

    def get_jackknifing_fields_list(self, fields: Fields) -> List[Fields]:
        """
        Creates the list of jackknifed fields from the input `fields`. The input `fields`
        contains all of the fields which will be used to evaluate this particular instance.
        This method needs to return a list of new `Fields` that will each be evaluated.

        For example, if the references need to be jackknived for the input:

            {"summary": summary, "references": [reference1, reference2, reference3]}

        The method would return a list of three instances:

            [
                {"summary": summary, "references": [reference1, reference2]},
                {"summary": summary, "references": [reference1, reference3]},
                {"summary": summary, "references": [reference2, reference3]}
            ]

        If the `fields` cannot be jackknived (for example, if the above input only provided
        one reference), `None` should be returned.

        Args:
            fields (Fields): The fields that should be jackknived.

        Returns (List[Fields]):
            The jackknifed list of fields
        """
        raise NotImplementedError


class ReferencesJackknifer(Jackknifer):
    """
    Jackknives the "references" field of type `ReferencesField`.
    """

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


class PyramidJackknifer(Jackknifer):
    """
    Jackknives the "pyramid" field of type `PyramidField`
    """
    @overrides
    def get_jackknifing_fields_list(self, fields: Fields) -> List[Fields]:
        pyramid: Pyramid = fields['pyramid'].pyramid
        if len(pyramid.summarizer_ids) == 1:
            # No jackknifing can be done, return `None`
            return None

        jk_fields_list = []
        for i in range(len(pyramid.summarizer_ids)):
            # Copy the original fields and replace the pyramid
            jk_fields = Fields(fields)
            jk_fields['pyramid'] = PyramidField(pyramid.remove_summary(i))
            jk_fields_list.append(jk_fields)
        return jk_fields_list
