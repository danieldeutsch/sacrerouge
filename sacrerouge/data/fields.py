from typing import Dict, List, Union


class Field(object):
    def __hash__(self) -> int:
        raise NotImplementedError

    def __eq__(self, other: 'Field') -> bool:
        raise NotImplementedError


class DocumentsField(Field):
    def __init__(self, documents: Union[List[str], List[List[str]]]) -> None:
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


class ReferencesField(Field):
    def __init__(self, references: Union[List[str], List[List[str]]]) -> None:
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


class SummaryField(Field):
    def __init__(self, summary: Union[str, List[str]]) -> None:
        self.summary = summary

    def __hash__(self) -> int:
        if isinstance(self.summary, list):
            return hash(tuple(self.summary))
        return hash(self.summary)

    def __eq__(self, other: 'SummaryField') -> bool:
        return self.summary == other.summary


class Fields(dict):
    def __init__(self, fields: Dict[str, Field]) -> None:
        for name, field in fields.items():
            assert isinstance(field, Field)
            self[name] = field

    def select_fields(self, names: List[str]) -> 'Fields':
        return Fields({name: self[name] for name in names})

    def __hash__(self) -> int:
        fields_tuple = tuple([self[name] for name in sorted(self.keys())])
        return hash(fields_tuple)
