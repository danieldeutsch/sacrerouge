import bisect
import os
import re
from lxml import etree
from typing import Dict, List, Set, Tuple


class Part(object):
    def __init__(self, text: str, start: int, end: int) -> None:
        self.text = text
        self.start = start
        self.end = end


class Contributor(object):
    def __init__(self, summary_index: int, label: str, parts: List[Part]) -> None:
        self.summary_index = summary_index
        self.label = label
        self.parts = parts


class ContributorAnnotation(object):
    def __init__(self, label: str, parts: List[Part]) -> None:
        self.label = label
        self.parts = parts


class SCU(object):
    def __init__(self, scu_id: int, label: str, contributors: List[Contributor]) -> None:
        self.scu_id = scu_id
        self.label = label
        self.contributors = contributors


class SCUAnnotation(object):
    def __init__(self, scu_id: int, label: str, contributors: List[ContributorAnnotation]) -> None:
        self.scu_id = scu_id
        self.label = label
        self.contributors = contributors


class Pyramid(object):
    def __init__(self,
                 instance_id: str,
                 summaries: List[str],
                 scus: List[SCU]) -> None:
        self.instance_id = instance_id
        self.summaries = summaries
        self.scus = scus

    @staticmethod
    def _load_summaries(root, default_document_regex: str = None):
        text = '\n'.join([node.text if node.text else '' for node in root.xpath('./text/line')])

        # The pyramid files contain regular expressions that match the tags
        # which indicate a summary is about to start. Therefore, the summaries are
        # in between the tags
        nodes = list(root.xpath('./startDocumentRegEx'))
        if len(nodes) == 0:
            # If the document regex doesn't exist due to an error, we use the default
            assert default_document_regex is not None
            document_start_regex = re.compile(default_document_regex)
        else:
            document_start_regex = re.compile(nodes[0].text)

        # The starts and ends of the summarys, not the header tags
        starts, ends = [], []
        for i, match in enumerate(document_start_regex.finditer(text)):
            start, end = match.span()
            # Find the first character of the summary
            while text[end].isspace():
                end += 1
            starts.append(end)
            if i != 0:
                ends.append(start)
        ends.append(len(text))

        summaries = [text[start:end].strip().replace('\n', ' ') for start, end in zip(starts, ends)]
        return summaries, starts

    @staticmethod
    def _load_scus(root,
                   summaries: List[str],
                   offsets: List[int]) -> List[SCU]:
        scus = []
        for node in root.xpath('scu'):
            label = node.get('label')
            scu_id = int(node.get('uid'))
            contributors = []
            for contrib_node in node.xpath('./contributor'):
                contrib_label = contrib_node.get('label')
                summary_indices = []
                parts = []
                for part_node in contrib_node.xpath('./part'):
                    text = part_node.get('label')
                    start = int(part_node.get('start'))
                    end = int(part_node.get('end'))

                    # if text in part_offset_errors:
                    #     start = part_offset_errors[text]['start']
                    #     end = part_offset_errors[text]['end']

                    summary_index = bisect.bisect_right(offsets, start) - 1
                    assert summary_index >= 0
                    summary_indices.append(summary_index)

                    # Make sure the label of the part is identical to the text from the summary
                    start -= offsets[summary_index]
                    end -= offsets[summary_index]
                    assert text == summaries[summary_index][start:end], (text, summaries[summary_index][start:end])

                    parts.append(Part(text, start, end))

                if len(set(summary_indices)) > 1:
                    print(f'SCU {scu_id} contributor "{contrib_label}" comes from multiple summaries. Skipping contributor')
                    continue
                else:
                    summary_index = summary_indices[0]

                contributors.append(Contributor(summary_index, contrib_label, parts))

            if len(contributors) == 0:
                # This could happen if all of the contributors are skipped due to errors
                print(f'SCU {scu_id} has 0 valid contributors. Skipping SCU')
                continue

            contributors_ok = len(contributors) == len(set([contributor.summary_index for contributor in contributors]))
            if not contributors_ok:
                print(f'SCU {scu_id} has multiple contributors with identical summary indices. Skipping SCU')
                continue

            scus.append(SCU(scu_id, label, contributors))
            assert len(contributors) <= len(offsets)

        return scus

    @staticmethod
    def from_xml(instance_id: str, file_path_or_xml: str) -> 'Pyramid':
        if os.path.exists(file_path_or_xml):
            xml = open(file_path_or_xml, 'r').read()
        else:
            xml = file_path_or_xml

        root = etree.fromstring(xml)
        summaries, offsets = Pyramid._load_summaries(root)
        scus = Pyramid._load_scus(root, summaries, offsets)
        return Pyramid(instance_id, summaries, scus)


class PyramidAnnotation(object):
    def __init__(self,
                 instance_id: str,
                 summarizer_id: str,
                 summarizer_type: str,
                 summary: str,
                 scus: List[SCU]) -> None:
        self.instance_id = instance_id
        self.summarizer_id = summarizer_id
        self.summarizer_type = summarizer_type
        self.summary = summary
        self.scus = scus

    @staticmethod
    def _load_summary(root) -> str:
        lines = []
        for node in root.xpath('./annotation/text/line'):
            if node.text:
                lines.append(node.text.strip())
        summary = ' '.join(lines)
        summary = re.sub(r'\s+', ' ', summary)
        return summary

    @staticmethod
    def _find_exact_matches(summary: str, text: str) -> List[int]:
        # Find all exact of the text in the summary. Return the list of offsets
        regex = re.escape(text)
        return [match.start() for match in re.finditer(regex, summary)]

    @staticmethod
    def _find_closest_match(matches: List[int], index: int) -> int:
        differences = [abs(match - index) for match in matches]
        min_diff = min(differences)
        min_index = differences.index(min_diff)
        start = matches[min_index]
        return start, min_index

    @staticmethod
    def _find_soft_matches(summary: str, text: str, start: int) -> Tuple[str, int]:
        # Many of the mismatches are due to weird whitespace issues, so we get rid
        # of the whitespace, find matches, and then remap to the summary

        # Maps from the character index in the summary without spaces to the
        # character index in the summary with spaces
        index_map = {}
        offset = 0
        for i, char in enumerate(summary):
            if char != ' ':
                index_map[offset] = i
                offset += 1

        edited_summary = summary.replace(' ', '')
        edited_text = text.replace(' ', '')

        regex = re.escape(edited_text)
        edited_starts = [match.start() for match in re.finditer(regex, edited_summary)]
        starts = [index_map[index] for index in edited_starts]

        start, index = PyramidAnnotation._find_closest_match(starts, start)
        end = index_map[edited_starts[index] + len(edited_text) - 1]
        found_text = summary[start:end + 1]

        return found_text, start

    @staticmethod
    def _load_scus(root, summary: str) -> List[SCUAnnotation]:
        scus = []
        # Iterate over all peerscu nodes with a contributor child, others
        # are not matches
        for node in root.xpath('./annotation/peerscu[contributor]'):
            label = node.get('label')
            scu_id = int(node.get('uid'))
            # SCU 0 is a catchall for non-matches
            if scu_id == 0:
                continue
            contributors = []
            for contributor_node in node.xpath('./contributor'):
                contrib_label = contributor_node.get('label')
                parts = []
                for part_node in contributor_node.xpath('./part'):
                    text = part_node.get('label')
                    text = re.sub(r'\s+', ' ', text)
                    start = int(part_node.get('start'))

                    matches = PyramidAnnotation._find_exact_matches(summary, text)
                    if len(matches) > 0:
                        # Find the match which is closest to "start"
                        found_text = text
                        start, _ = PyramidAnnotation._find_closest_match(matches, start)
                    elif len(matches) == 0:
                        found_text, start = PyramidAnnotation._find_soft_matches(summary, text, start)

                    end = start + len(found_text)
                    assert summary[start:end] == found_text
                    parts.append(Part(found_text, start, end))

                contributors.append(ContributorAnnotation(contrib_label, parts))
            scus.append(SCUAnnotation(scu_id, label, contributors))

        return scus

    @staticmethod
    def from_xml(instance_id: str, summarizer_id: str, summarizer_type: str, file_path_or_xml: str) -> 'PyramidAnnotation':
        if os.path.exists(file_path_or_xml):
            xml = open(file_path_or_xml, 'r').read()
        else:
            xml = file_path_or_xml

        root = etree.fromstring(xml)
        summary = PyramidAnnotation._load_summary(root)
        scus = PyramidAnnotation._load_scus(root, summary)
        return PyramidAnnotation(instance_id, summarizer_id, summarizer_type, summary, scus)
