from spacy.tokens import Token
from typing import List

from sacrerouge.metrics.decomposed_rouge.categorizers import Categorizer


class NERCategorizer(Categorizer):
    def __init__(self, name: str, tag_sets: List[List[str]]):
        super().__init__(name)
        self.tag_sets = [set(tags) for tags in tag_sets]

    def is_match(self, token1: Token, token2: Token) -> bool:
        for tags in self.tag_sets:
            if token1.ent_type_ in tags and token2.ent_type_ in tags:
                return True
        return False

    def is_candidate(self, token: Token) -> bool:
        for tags in self.tag_sets:
            if token.ent_type_ in tags:
                return True
        return False
