import spacy
from collections import namedtuple
from spacy.tokens import Span
from typing import List

NP_CHUNKS_STRATEGY = 'np-chunks'
MAX_NP_STRATEGY = 'max-np'
NER_STRATEGY = 'ner'
ALL_STRATEGY = 'all'
STRATEGIES = [NP_CHUNKS_STRATEGY, MAX_NP_STRATEGY, NER_STRATEGY, ALL_STRATEGY]

AnswerOffsets = namedtuple('Answer', ['start', 'end', 'sent_start', 'sent_end'])


class AnswerSelector(object):
    def __init__(self, strategy: str):
        if strategy not in STRATEGIES:
            raise Exception(f'Unknown strategy: {strategy}')
        self.strategy = strategy
        self.nlp = spacy.load('en_core_web_sm')

    def _get_np_chunks_answers(self, sentence: Span) -> List[AnswerOffsets]:
        chunks = []
        for chunk in sentence.noun_chunks:
            chunks.append(AnswerOffsets(chunk.start_char, chunk.end_char, sentence.start_char, sentence.end_char))
        return chunks

    def _get_max_np_answers(self, sentence: Span) -> List[AnswerOffsets]:
        root = sentence.root
        nodes = [root]
        nps = []

        while len(nodes) > 0:
            node = nodes.pop()

            # If the node is a noun, collect all of the tokens
            # which are descendants of this node
            recurse = True
            if node.pos_ in ['NOUN', 'PROPN']:
                min_index = node.i
                max_index = node.i
                stack = [node]
                while len(stack) > 0:
                    current = stack.pop()
                    min_index = min(min_index, current.i)
                    max_index = max(max_index, current.i)
                    for child in current.children:
                        stack.append(child)

                sent_start_index = sentence[0].i

                # Because of parsing issues, we only take NPs if they are shorter than a given length
                num_tokens = max_index - min_index + 1
                if num_tokens <= 7:
                    recurse = False
                    span = sentence[min_index - sent_start_index:max_index + 1 - sent_start_index]
                    nps.append(AnswerOffsets(span.start_char, span.end_char, sentence.start_char, sentence.end_char))

            if recurse:
                # Otherwise, process all of this node's children
                for child in node.children:
                    nodes.append(child)

        # Sort in order of appearance
        nps.sort(key=lambda offsets: offsets.start)
        return nps

    def _get_ner_answers(self, sentence: Span) -> List[AnswerOffsets]:
        ners = []
        for entity in sentence.ents:
            if entity.label_ in ['PERSON', 'NORP', 'FAC', 'ORG', 'GPE', 'LOC', 'EVENT', 'WORK_OF_ART']:
                ners.append(AnswerOffsets(entity.start_char, entity.end_char, sentence.start_char, sentence.end_char))
        return ners

    def _get_all_answers(self, sentence: Span) -> List[AnswerOffsets]:
        answers = set()
        answers |= set(self._get_np_chunks_answers(sentence))
        answers |= set(self._get_max_np_answers(sentence))
        answers |= set(self._get_ner_answers(sentence))

        # Sort in order of appearance
        answers = sorted(answers, key=lambda answer: (answer.start, answer.end))
        return answers

    def select(self, text: str) -> List[AnswerOffsets]:
        doc = self.nlp(text)
        answers = []
        for sent in doc.sents:
            if self.strategy == NP_CHUNKS_STRATEGY:
                answers.extend(self._get_np_chunks_answers(sent))
            elif self.strategy == MAX_NP_STRATEGY:
                answers.extend(self._get_max_np_answers(sent))
            elif self.strategy == NER_STRATEGY:
                answers.extend(self._get_ner_answers(sent))
            elif self.strategy == ALL_STRATEGY:
                answers.extend(self._get_all_answers(sent))
            else:
                raise Exception(f'Unknown strategy: {self.strategy}')
        return answers