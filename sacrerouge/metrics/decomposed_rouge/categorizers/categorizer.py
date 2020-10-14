from spacy.tokens import Token
from typing import Dict, List, Tuple

from sacrerouge.data import MetricsDict
from sacrerouge.metrics.decomposed_rouge.categorizers.util import calculate_maximum_matching


class Categorizer(object):
    def __init__(self, name: str) -> None:
        self.name = name

    def is_match(self, token1: Token, token2: Token) -> bool:
        raise NotImplementedError

    def is_candidate(self, token: Token) -> bool:
        raise NotImplementedError

    def select_matches(self,
                       summary_tokens: List[Token],
                       reference_tokens: List[Token],
                       matches: List[Tuple[int, int]],
                       intersection: int):
        common_matches = []
        for i, j in matches:
            summary_token = summary_tokens[i]
            reference_token = reference_tokens[j]
            if self.is_match(summary_token, reference_token):
                common_matches.append((i, j, 1.0))

        num_matches = calculate_maximum_matching(common_matches)
        num_summary_tokens = sum(1 for token in summary_tokens if self.is_candidate(token))
        num_reference_tokens = sum(1 for token in reference_tokens if self.is_candidate(token))

        precision = num_matches / num_summary_tokens * 100 if num_summary_tokens > 0 else 0
        recall = num_matches / num_reference_tokens * 100 if num_reference_tokens > 0 else 0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        contribution = num_matches / intersection * 100 if len(matches) > 0 else 0

        return MetricsDict({
            self.name: {
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'contribution': contribution
            }
        })


class TupleCategorizer(Categorizer):
    def get_tuples(self, tokens: List[Token]) -> List[Dict[str, int]]:
        raise NotImplementedError

    def select_matches(self,
                       summary_tokens: List[Token],
                       reference_tokens: List[Token],
                       matches: List[Tuple[int, int]],
                       intersection: int):
        summary_tuples = self.get_tuples(summary_tokens)
        reference_tuples = self.get_tuples(reference_tokens)
        matches = set(matches)

        # Figure out the list of tuple-level matches based on whether the tuples
        # match each other completely
        tuple_matches = []
        for s_i, summary_tuple in enumerate(summary_tuples):
            for r_j, reference_tuple in enumerate(reference_tuples):
                assert len(summary_tuple) == len(reference_tuple)
                # See if each component of these two tuples can be aligned
                matched = True
                for key, i in summary_tuple.items():
                    if key not in reference_tuple:
                        matched = False
                        break
                    j = reference_tuple[key]
                    if (i, j) not in matches:
                        matched = False
                        break

                if matched:
                    tuple_matches.append((s_i, r_j, len(summary_tuple)))

        # Calculate the weight of the matched tuples, only allowing each tuple to be matched once.
        # The tuples form an equivalence class, so it doesn't matter exactly what match we use. This is
        # equivalent to calculating the size of the maximum matching in a bipartite graph where the
        # two disjoint sets of vertices are the summary and reference tuples, and an edge exists between
        # them if they were matched
        total_weight = calculate_maximum_matching(tuple_matches)

        summary_tuples_weight = sum(len(tup) for tup in summary_tuples)
        reference_tuples_weight = sum(len(tup) for tup in reference_tuples)

        precision = total_weight / summary_tuples_weight * 100 if summary_tuples_weight > 0 else 0
        recall = total_weight / reference_tuples_weight * 100 if reference_tuples_weight > 0 else 0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        contribution = total_weight / intersection * 100 if len(matches) > 0 else 0

        return MetricsDict({
            self.name: {
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'contribution': contribution
            }
        })