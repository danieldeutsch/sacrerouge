import bisect
import os
import re
from lxml import etree
from typing import List, Set, Tuple


def _find_closest_match(matches: List[int], index: int) -> int:
    differences = [abs(match - index) for match in matches]
    min_diff = min(differences)
    min_index = differences.index(min_diff)
    start = matches[min_index]
    return start, min_index


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
    if len(edited_starts) == 0:
        return None, None
    starts = [index_map[index] for index in edited_starts]

    start, index = _find_closest_match(starts, start)
    end = index_map[edited_starts[index] + len(edited_text) - 1]
    found_text = summary[start:end + 1]

    return found_text, start


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

    def get_weight(self) -> int:
        """Calculates the weight of the SCU"""
        # We don't keep this as a data member because then it would be serialized to the json. That's probably
        # an OK thing to do, but we have many already-created serialized pyramids, and adding that might break them.
        #
        # This should be just the length, but we take the unique number because there were many errors in the
        # DUC/TAC pyramid files which may make that assumption false.
        return len(set(contributor.summary_index for contributor in self.contributors))


class SCUAnnotation(object):
    def __init__(self, scu_id: int, label: str, contributors: List[ContributorAnnotation]) -> None:
        self.scu_id = scu_id
        self.label = label
        self.contributors = contributors


class Pyramid(object):
    def __init__(self,
                 instance_id: str,
                 summaries: List[str],
                 summarizer_ids: List[str],
                 scus: List[SCU]) -> None:
        self.instance_id = instance_id
        self.summaries = summaries
        self.summarizer_ids = summarizer_ids
        self.scus = scus

    def remove_summary(self, index: int) -> 'Pyramid':
        new_summaries = self.summaries[:index] + self.summaries[index + 1:]
        new_summarizer_ids = self.summarizer_ids[:index] + self.summarizer_ids[index + 1:]
        new_scus = []
        for scu in self.scus:
            contributors = []
            for contributor in scu.contributors:
                if contributor.summary_index != index:
                    # Potentially fix the summary index
                    summary_index = contributor.summary_index
                    if summary_index > index:
                        summary_index -= 1

                    contributors.append(Contributor(summary_index, contributor.label, contributor.parts))
            if len(contributors) > 0:
                new_scus.append(SCU(scu.scu_id, scu.label, contributors))
        return Pyramid(self.instance_id, new_summaries, new_summarizer_ids, new_scus)

    def get_annotation(self, index: int) -> 'PyramidAnnotation':
        scus = []
        for scu in self.scus:
            new_contributors = []
            for contributor in scu.contributors:
                if contributor.summary_index == index:
                    new_contributors.append(ContributorAnnotation(contributor.label, contributor.parts))
            if len(new_contributors) > 0:
                scus.append(SCUAnnotation(scu.scu_id, scu.label, new_contributors))
        return PyramidAnnotation(self.instance_id, self.summarizer_ids[index], 'reference', self.summaries[index], scus)

    def get_scu_id_set(self, index: int) -> Set[int]:
        scus = set()
        for i in range(len(self.summaries)):
            for scu in self.scus:
                for contributor in scu.contributors:
                    if contributor.summary_index == index:
                        scus.add(scu.scu_id)
        return scus

    @staticmethod
    def _get_summarizer_id(title_regex_match: str) -> str:
        # Remove any leading or trailing spaces or '-'
        start = 0
        while title_regex_match[start] in [' ', '-', '\n']:
            start += 1
        end = len(title_regex_match) - 1
        while title_regex_match[end] in [' ', '-', '\n']:
            end -= 1

        filename = title_regex_match[start:end + 1]
        columns = filename.split('.')
        return columns[-1]

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

        # The starts and ends of the summaries, not the header tags
        starts, ends = [], []
        summarizer_ids = []
        for i, match in enumerate(document_start_regex.finditer(text)):
            if match.group(0).strip():
                summarizer_ids.append(Pyramid._get_summarizer_id(match.group(0)))
                start, end = match.span()
                # Find the first character of the summary
                while text[end].isspace():
                    end += 1
                starts.append(end)
                if i != 0:
                    ends.append(start)
        ends.append(len(text))

        summaries = [text[start:end].strip().replace('\n', ' ') for start, end in zip(starts, ends)]
        for summary in summaries:
            assert len(summary.strip()) > 0
        return summaries, starts, summarizer_ids

    @staticmethod
    def _load_scus(root,
                   summaries: List[str],
                   offsets: List[int]) -> List[SCU]:
        scus = []
        for node in root.xpath('scu'):
            label = node.get('label')
            # Some labels have endings like "(2.1)"
            label = re.sub(r' \(\d+\.\d+\)$', '', label)

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

                    summary_index = bisect.bisect_right(offsets, start) - 1
                    assert summary_index >= 0
                    summary_indices.append(summary_index)

                    # Make sure the label of the part is identical to the text from the summary
                    start -= offsets[summary_index]
                    end -= offsets[summary_index]
                    if text != summaries[summary_index][start:end]:
                        found_text, start = _find_soft_matches(summaries[summary_index], text, start)
                        end = start + len(found_text)
                        text = found_text

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
    def from_xml(instance_id: str,
                 file_path_or_xml: str,
                 default_document_regex: str = None) -> 'Pyramid':
        if os.path.exists(file_path_or_xml):
            xml = open(file_path_or_xml, 'r').read()
        else:
            xml = file_path_or_xml

        root = etree.fromstring(xml)
        summaries, offsets, summarizer_ids = Pyramid._load_summaries(root, default_document_regex=default_document_regex)
        scus = Pyramid._load_scus(root, summaries, offsets)
        return Pyramid(instance_id, summaries, summarizer_ids, scus)


class PyramidAnnotation(object):
    def __init__(self,
                 instance_id: str,
                 summarizer_id: str,
                 summarizer_type: str,
                 summary: str,
                 scus: List[SCUAnnotation]) -> None:
        self.instance_id = instance_id
        self.summarizer_id = summarizer_id
        self.summarizer_type = summarizer_type
        self.summary = summary
        self.scus = scus

    def get_scu_id_set(self) -> Set[int]:
        return set([scu.scu_id for scu in self.scus])

    @staticmethod
    def _load_summary(root) -> str:
        lines = []
        for node in root.xpath('./annotation/text/line'):
            if node.text:
                lines.append(node.text.strip())
        summary = ' '.join(lines)
        summary = re.sub(r'\s+', ' ', summary).strip()
        return summary

    @staticmethod
    def _find_exact_matches(summary: str, text: str) -> List[int]:
        # Find all exact of the text in the summary. Return the list of offsets
        regex = re.escape(text)
        return [match.start() for match in re.finditer(regex, summary)]

    @staticmethod
    def _load_scus(root, summary: str, pyramid: Pyramid) -> List[SCUAnnotation]:
        # Because of parsing errors for the original pyramid, there may be some SCUs
        # which are no longer valid (because they were dropped in the parsing). We
        # will skip those
        known_scu_ids = set([scu.scu_id for scu in pyramid.scus])

        scus = []
        # Iterate over all peerscu nodes with a contributor child, others
        # are not matches
        for node in root.xpath('./annotation/peerscu[contributor]'):
            label = node.get('label')
            label = re.sub(r'^\(\d+\) ', '', label)
            label = re.sub(r' \(\d+\.\d+\)$', '', label)

            scu_id = int(node.get('uid'))
            if scu_id not in known_scu_ids:
                continue

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
                        start, _ = _find_closest_match(matches, start)
                    elif len(matches) == 0:
                        found_text, start = _find_soft_matches(summary, text, start)
                        if found_text is None:
                            print(f'Could not find part "{text}" for SCU {scu_id}. Skipping')
                            continue

                    end = start + len(found_text)
                    assert summary[start:end] == found_text
                    parts.append(Part(found_text, start, end))

                if len(parts) == 0:
                    print(f'No parts for contributor of SCU {scu_id}. Skipping')
                else:
                    contributors.append(ContributorAnnotation(contrib_label, parts))

            if len(contributors) == 0:
                print(f'No contributors for SCU {scu_id}. Skipping')
            else:
                scus.append(SCUAnnotation(scu_id, label, contributors))

        return scus

    @staticmethod
    def from_xml(instance_id: str,
                 summarizer_id: str,
                 summarizer_type: str,
                 file_path_or_xml: str,
                 pyramid: Pyramid) -> 'PyramidAnnotation':
        if os.path.exists(file_path_or_xml):
            xml = open(file_path_or_xml, 'r').read()
        else:
            xml = file_path_or_xml

        root = etree.fromstring(xml)
        summary = PyramidAnnotation._load_summary(root)
        if len(summary) == 0:
            # For some reason, there are blank summaries in some files
            # (see TAC 2008, D0805-A.M.100.A.5)
            print(f'Summary for instance {instance_id} and summarizer {summarizer_id} is `None`')
            return None
        scus = PyramidAnnotation._load_scus(root, summary, pyramid)
        return PyramidAnnotation(instance_id, summarizer_id, summarizer_type, summary, scus)
