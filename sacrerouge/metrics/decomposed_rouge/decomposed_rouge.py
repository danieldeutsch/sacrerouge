import argparse
import logging
import os
import spacy
from collections import defaultdict
from nltk.stem import PorterStemmer
from overrides import overrides
from spacy.tokens import Token
from subprocess import Popen
from typing import Dict, List, Set, Tuple

from sacrerouge.commands import MetricSetupSubcommand
from sacrerouge.common import DATA_ROOT
from sacrerouge.data import MetricsDict
from sacrerouge.data.types import ReferenceType, SummaryType
from sacrerouge.metrics import Metric, ReferenceBasedMetric
from sacrerouge.metrics.decomposed_rouge.categorizers import DependencyCategorizer, DependencyVerbRelationsCategorizer, \
    NERCategorizer, NPChunkCategorizer, POSCategorizer, StopwordCategorizer
from sacrerouge.metrics.decomposed_rouge.categorizers.util import calculate_maximum_matching

logger = logging.getLogger(__name__)

# The text which should be used to match other tokens (could be the original token
# or the stem, for example)
Token.set_extension('matching_text', default=None)

# A flag which marks whether this token is eligible for matching
Token.set_extension('is_matchable', default=None)

# The token's index in the list of tokens generated from the document
Token.set_extension('index', default=None)

# A flag which marks if the token is part of a noun phrase
Token.set_extension('is_np', default=None)


@Metric.register('decomposed-rouge')
class DecomposedRouge(ReferenceBasedMetric):
    def __init__(self,
                 rouge_data_dir: str = f'{DATA_ROOT}/metrics/ROUGE-1.5.5/data',
                 remove_stopwords: bool = False,
                 use_porter_stemmer: bool = True,
                 pretokenized_text: bool = False):
        super().__init__()
        self.rouge_data_dir = rouge_data_dir
        self.remove_stopwords = remove_stopwords
        self.use_porter_stemmer = use_porter_stemmer
        self.pretokenized_text = pretokenized_text

        self.stemmer = PorterStemmer(PorterStemmer.ORIGINAL_ALGORITHM)
        self.stemmer_exceptions = self._load_stemmer_exceptions(rouge_data_dir)
        self.stopwords = self._load_stopwords(rouge_data_dir)
        self.nlp = spacy.load('en_core_web_sm')

        self.categorizers = [
            NERCategorizer('ner', [['PERSON'], ['NORP', 'ORG'], ['GPE', 'LOC']]),
            POSCategorizer('pos-adj', ['ADJ']),
            POSCategorizer('pos-verb', ['VERB']),
            POSCategorizer('pos-noun', ['NOUN']),
            POSCategorizer('pos-propn', ['PROPN']),
            POSCategorizer('pos-adv', ['ADV']),
            POSCategorizer('pos-num', ['NUM']),
            DependencyCategorizer('dep-root', ['ROOT']),
            DependencyCategorizer('dep-nsubj', ['nsubj']),
            DependencyCategorizer('dep-dobj', ['dobj']),
            NPChunkCategorizer(),
            DependencyVerbRelationsCategorizer('dep-verb+nsubj', ['nsubj']),
            DependencyVerbRelationsCategorizer('dep-verb+dobj', ['dobj']),
            DependencyVerbRelationsCategorizer('dep-verb+nsubj+dobj', ['nsubj', 'dobj']),
            StopwordCategorizer(self.rouge_data_dir)
        ]

    def _load_stemmer_exceptions(self, root: str) -> Dict[str, str]:
        exceptions = {}
        for filename in ['adj.exc', 'adv.exc', 'noun.exc', 'verb.exc']:
            file_path = os.path.join(root, 'WordNet-2.0-Exceptions', filename)
            with open(file_path, 'r') as f:
                for line in f:
                    # I think there is a bug in the original perl script
                    # to construct the exceptions database. Some of the lines
                    # have more than 2 words on them, but the script only
                    # maps the first to the second, ignoring the third.
                    columns = line.strip().split()
                    exceptions[columns[0]] = columns[1]
        return exceptions

    def _load_stopwords(self, root: str) -> Set[str]:
        file_path = os.path.join(root, 'smart_common_words.txt')
        return set(open(file_path, 'r').read().splitlines())

    def _preprocess_summary(self, summary: SummaryType) -> List[Token]:
        # The analysis doesn't pay attention to sentences, so we just wrap the string summary into
        # a list of sentences so the code runs the same regardless if the input is a string or a list of strings
        if isinstance(summary, str):
            summary = [summary]

        tokens = []
        for sentence in summary:
            if self.pretokenized_text:
                doc = self.nlp.tokenizer.tokens_from_list(sentence.split())
                self.nlp.tagger(doc)
                self.nlp.parser(doc)
                self.nlp.entity(doc)
            else:
                doc = self.nlp(sentence)

            for token in doc:
                text = token.text.lower()
                # There are some whitespace only tokens. I don't know where they come from
                if len(text.strip()) == 0:
                    continue

                is_matchable = True
                if self.remove_stopwords and text in self.stopwords:
                    is_matchable = False
                elif self.use_porter_stemmer and len(text) > 3:
                    if text in self.stemmer_exceptions:
                        text = self.stemmer_exceptions[text]
                    else:
                        text = self.stemmer.stem(text)

                token._.matching_text = text
                token._.is_matchable = is_matchable and not token.is_punct
                token._.index = len(tokens)
                tokens.append(token)

            for chunk in doc.noun_chunks:
                for token in chunk:
                    token._.is_np = True

        return tokens

    def _preprocess_all(self, summaries_list: List[List[str]]):
        tokens_lists = []
        for summaries in summaries_list:
            tokens_lists.append([])
            for summary in summaries:
                tokens_lists[-1].append(self._preprocess_summary(summary))
        return tokens_lists

    def _group_by_token(self, tokens: List[Token]) -> Dict[str, List[int]]:
        groups = defaultdict(list)
        for token in tokens:
            if token._.is_matchable:
                groups[token._.matching_text].append(token._.index)
        return groups

    def _get_matches(self,
                     summary_tokens: List[Token],
                     reference_tokens_list: List[List[Token]]) -> List[List[Tuple[int, int]]]:
        summary_groups = self._group_by_token(summary_tokens)
        reference_groups_list = [self._group_by_token(reference_tokens) for reference_tokens in reference_tokens_list]
        matches_list = []
        for reference_groups in reference_groups_list:
            matches_list.append([])
            for token in summary_groups.keys():
                if token in reference_groups:
                    summary_indices = summary_groups[token]
                    reference_indices = reference_groups[token]
                    for i in summary_indices:
                        for j in reference_indices:
                            matches_list[-1].append((i, j))
        return matches_list

    def _score_with_categorizers(self,
                                 summary_tokens: List[Token],
                                 reference_tokens_list: List[List[Token]],
                                 matches_list: List[List[Tuple[int, int]]]) -> MetricsDict:
        # This will be used to calculate the standard ROUGE score
        total_intersection = 0
        total_summary_tokens = 0
        total_reference_tokens = 0

        # This will hold the category-specific metrics
        category_metrics_list = [[] for _ in self.categorizers]

        for reference_tokens, matches in zip(reference_tokens_list, matches_list):
            weighted_matches = [(i, j, 1) for i, j in matches]
            intersection = calculate_maximum_matching(weighted_matches)
            total_intersection += intersection
            total_summary_tokens += len(summary_tokens)
            total_reference_tokens += len(reference_tokens)

            for i, categorizer in enumerate(self.categorizers):
                category_metrics_list[i].append(categorizer.select_matches(summary_tokens, reference_tokens, matches, intersection))

        # Calculate the ROUGE-1 score
        precision = total_intersection / total_summary_tokens * 100 if total_summary_tokens > 0 else 0
        recall = total_intersection / total_reference_tokens * 100 if total_reference_tokens > 0 else 0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        metrics = MetricsDict({
            'decomposed-rouge': {
                'rouge-1': {
                    'precision': precision,
                    'recall': recall,
                    'f1': f1
                }
            }
        })

        # Average the category metrics together
        for category_metrics in category_metrics_list:
            metrics['decomposed-rouge'].update(sum(category_metrics) / len(category_metrics))

        return metrics

    def score_multi_all(self,
                        summaries_list: List[List[SummaryType]],
                        references_list: List[ReferenceType],
                        **kwargs) -> List[List[MetricsDict]]:
        num_summaries = sum(len(summaries) for summaries in summaries_list)
        count = 0

        metrics_list = []
        for summaries, references in zip(summaries_list, references_list):
            metrics_list.append([])
            reference_tokens_list = [self._preprocess_summary(reference) for reference in references]
            for summary in summaries:
                summary_tokens = self._preprocess_summary(summary)
                matches_list = self._get_matches(summary_tokens, reference_tokens_list)
                metrics_list[-1].append(self._score_with_categorizers(summary_tokens, reference_tokens_list, matches_list))

                count += 1
                if count % 100 == 0:
                    logger.info(f'Processed {count} / {num_summaries} summaries')
        logger.info('Finished processing summaries')

        return metrics_list


@MetricSetupSubcommand.register('decomposed-rouge')
class DecomposedRougeSetupSubcommand(MetricSetupSubcommand):
    @overrides
    def add_subparser(self, parser: argparse._SubParsersAction):
        description = 'Setup the Decomposed ROGUE metric'
        self.parser = parser.add_parser('decomposed-rouge', description=description, help=description)
        self.parser.set_defaults(subfunc=self.run)

    @overrides
    def run(self, args):
        logger.info(f'Downloading Spacy model en_core_web_sm')
        command = 'python -m spacy download en_core_web_sm'
        process = Popen(command, shell=True)
        process.communicate()
        if process.returncode != 0:
            print('DecomposedRouge setup failure')
        else:
            print('DecomposedRouge setup success')