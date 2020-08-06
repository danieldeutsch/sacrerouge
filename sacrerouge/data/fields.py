from typing import Any, Dict, List

from sacrerouge.data.pyramid import Pyramid, PyramidAnnotation
from sacrerouge.data.types import DocumentType, ReferenceType, SummaryType


class Field(object):
    def __hash__(self) -> int:
        raise NotImplementedError

    def __eq__(self, other: 'Field') -> bool:
        raise NotImplementedError

    def to_input(self) -> Any:
        """Returns what should be passed as input to the evaluation metric."""
        raise NotImplementedError


class DocumentsField(Field):
    def __init__(self, documents: List[DocumentType]) -> None:
        self.documents = documents

    def __hash__(self) -> int:
        hashes = []
        for document in self.documents:
            if isinstance(document, list):
                hashes.append(hash(tuple(document)))
            else:
                hashes.append(hash(document))
        return hash(tuple(hashes))

    def __eq__(self, other: 'DocumentsField') -> bool:
        return self.documents == other.documents

    def to_input(self) -> List[DocumentType]:
        return self.documents


class PyramidField(Field):
    def __init__(self, pyramid: Pyramid) -> None:
        self.pyramid = pyramid

    def __hash__(self) -> int:
        hashes = []
        hashes.append(hash(self.pyramid.instance_id))
        for summarizer_id in self.pyramid.summarizer_ids:
            hashes.append(hash(summarizer_id))
        return hash(tuple(hashes))

    def __eq__(self, other: 'PyramidField') -> bool:
        return self.pyramid.instance_id == other.pyramid.instance_id and \
               self.pyramid.summarizer_ids == other.pyramid.summarizer_ids

    def to_input(self) -> Pyramid:
        return self.pyramid


class PyramidAnnotationField(Field):
    def __init__(self, annotation: PyramidAnnotation) -> None:
        self.annotation = annotation

    def __hash__(self) -> int:
        return hash(tuple([self.annotation.instance_id, self.annotation.summarizer_id]))

    def __eq__(self, other: 'PyramidAnnotationField') -> bool:
        return self.annotation.instance_id == other.annotation.instance_id and \
               self.annotation.summarizer_id == other.annotation.summarizer_id

    def to_input(self) -> PyramidAnnotation:
        return self.annotation


class ReferencesField(Field):
    def __init__(self, references: List[ReferenceType]) -> None:
        self.references = references

    def __hash__(self) -> int:
        hashes = []
        for reference in self.references:
            if isinstance(reference, list):
                hashes.append(hash(tuple(reference)))
            else:
                hashes.append(hash(reference))
        return hash(tuple(hashes))

    def __eq__(self, other: 'ReferencesField') -> bool:
        return self.references == other.references

    def to_input(self) -> List[ReferenceType]:
        return self.references


class SummaryField(Field):
    def __init__(self, summary: SummaryType) -> None:
        self.summary = summary

    def __hash__(self) -> int:
        if isinstance(self.summary, list):
            return hash(tuple(self.summary))
        return hash(self.summary)

    def __eq__(self, other: 'SummaryField') -> bool:
        return self.summary == other.summary

    def to_input(self) -> SummaryType:
        return self.summary


class Fields(dict):
    def __init__(self, fields: Dict[str, Field]) -> None:
        super().__init__()
        for name, field in fields.items():
            assert isinstance(field, Field)
            self[name] = field

    def select_fields(self, names: List[str]) -> 'Fields':
        return Fields({name: self[name] for name in names})

    def __hash__(self) -> int:
        fields_tuple = tuple([self[name] for name in sorted(self.keys())])
        return hash(fields_tuple)
