from spacy.tokens import Token
from typing import Dict, List

from sacrerouge.metrics.decomposed_rouge.categorizers import Categorizer, TupleCategorizer


class DependencyCategorizer(Categorizer):
    def __init__(self, name: str, relations: List[str]):
        super().__init__(name)
        self.relations = set(relations)

    def is_match(self, token1: Token, token2: Token) -> bool:
        return token1.dep_ in self.relations and token2.dep_ in self.relations

    def is_candidate(self, token: Token) -> bool:
        return token.dep_ in self.relations


class DependencyVerbRelationsCategorizer(TupleCategorizer):
    def __init__(self, name: str, relations: List[str]) -> None:
        super().__init__(name)
        self.relations = set(relations)

    def _get_children(self, tokens: List[Token], head: Token) -> List[Token]:
        children = []
        for token in tokens:
            if token.head == head:
                children.append(token)
        return children

    def get_tuples(self, tokens: List[Token]) -> List[Dict[str, int]]:
        tuples = []
        for token in tokens:
            if token.pos_ == 'VERB':
                children = self._get_children(tokens, token)

                # Filter to only children with tags we care about
                children = list(filter(lambda child: child.dep_ in self.relations, children))

                # If the remaining children have the same set of relations that we're
                # looking for, we keep the match. Otherwise, I don't know what to do
                if len(self.relations) == len(set(child.dep_ for child in children)):
                    match = {'VERB': token._.index}
                    for child in children:
                        match[child.dep_] = child._.index
                    tuples.append(match)

        return tuples
