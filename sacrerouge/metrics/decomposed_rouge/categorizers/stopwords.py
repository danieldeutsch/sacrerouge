from spacy.tokens import Token

from sacrerouge.metrics.decomposed_rouge.categorizers import Categorizer


class StopwordCategorizer(Categorizer):
    def __init__(self, data_dir: str):
        super().__init__('stopwords')
        self.stopwords = set(open(f'{data_dir}/smart_common_words.txt', 'r').read().splitlines())

    def is_match(self, token1: Token, token2: Token) -> bool:
        return token1.text.lower() in self.stopwords and token2.text.lower() in self.stopwords

    def is_candidate(self, token: Token) -> bool:
        return token.text.lower() in self.stopwords
