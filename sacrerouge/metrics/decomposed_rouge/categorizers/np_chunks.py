from spacy.tokens import Token

from sacrerouge.metrics.decomposed_rouge.categorizers import Categorizer


class NPChunkCategorizer(Categorizer):
    def __init__(self):
        super().__init__('np-chunks')

    def is_match(self, token1: Token, token2: Token) -> bool:
        return token1._.is_np is True and token2._.is_np is True

    def is_candidate(self, token: Token) -> bool:
        return token._.is_np is True
