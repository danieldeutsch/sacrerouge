from spacy.tokens import Token
from typing import List

from sacrerouge.metrics.decomposed_rouge.categorizers import Categorizer


class POSCategorizer(Categorizer):
    def __init__(self, name: str, tags: List[str]):
        super().__init__(name)
        self.tags = set(tags)

    def is_match(self, token1: Token, token2: Token) -> bool:
        return token1.pos_ in self.tags and token2.pos_ in self.tags

    def is_candidate(self, token: Token) -> bool:
        return token.pos_ in self.tags
