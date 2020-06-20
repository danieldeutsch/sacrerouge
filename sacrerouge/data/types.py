from typing import List, Union

# These are all the same type, but I think it enhances readability
# to have a different type for each one.
DocumentType = Union[str, List[str]]
ReferenceType = Union[str, List[str]]
SummaryType = Union[str, List[str]]
