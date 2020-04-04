import argparse
import tarfile
from collections import defaultdict
from typing import Dict, List

from sacrerouge.data import Pyramid, PyramidAnnotation
from sacrerouge.io import JsonlWriter


def load_pyramids(pyramid_tar: str) -> Dict[str, Dict[str, Pyramid]]:
    pyramids = {}
    with tarfile.open(pyramid_tar, 'r') as tar:
        for member in tar.getmembers():
            if member.isfile() and member.name.startswith('allpyramids/'):
                path = member.name.split('/')
                filename = path[-1]
                instance_id = filename.split('.')[0].lower()

                xml = tar.extractfile(member).read().decode()
                pyramid = Pyramid.from_xml(f'{instance_id}', xml, default_document_regex='[-]*\n(\s*)D[0-9]*\.M\.250\.[A-Z]\.[A-Z]\n[-]*\n')
                pyramids[instance_id] = pyramid

    return pyramids


def load_peer_pyramids(eval_tar: str, pyramids: Dict[str, Dict[str, Pyramid]]) -> Dict[str, Dict[str, Dict[str, PyramidAnnotation]]]:
    annotations = defaultdict(dict)
    multiples = defaultdict(list)
    with tarfile.open(eval_tar, 'r') as tar:
        for member in tar.getmembers():
            if member.isfile() and member.name.startswith('allpans/'):
                path = member.name.split('/')
                filename = path[-1]
                parts = filename.split('.')
                number = parts[0]
                instance_id = parts[1].lower()
                summarizer_id = parts[5]
                # This directory only has peers
                assert not summarizer_id.isalpha()
                summarizer_type = 'peer'

                pyramid = pyramids[instance_id]
                xml = tar.extractfile(member).read().decode()
                annotation = PyramidAnnotation.from_xml(f'{instance_id}', summarizer_id, summarizer_type, xml, pyramid)
                if annotation:
                    if instance_id == 'd0631':
                        # This instance was annotated twice. We just take the first set
                        # for the pyramids files, but save both for a separate file
                        if number == '114':
                            annotations[instance_id][summarizer_id] = annotation
                        multiples[summarizer_id].append(annotation)
                    else:
                        annotations[instance_id][summarizer_id] = annotation
                else:
                    print(f'Annotation for {instance_id}, {summarizer_id} is `None`. Skipping')

    return annotations, multiples


def save_pyramids(pyramids: Dict[str, Pyramid],
                  output_dir: str) -> None:
    with JsonlWriter(f'{output_dir}/task1.pyramids.jsonl') as out:
        for instance_id in sorted(pyramids.keys()):
            pyramid = pyramids[instance_id]
            out.write(pyramid)


def save_peer_pyramids(annotations: Dict[str, Dict[str, PyramidAnnotation]],
                       output_dir: str) -> None:
    with JsonlWriter(f'{output_dir}/task1.pyramid-annotations.jsonl') as out:
        for instance_id in sorted(annotations.keys()):
            for summarizer_id in sorted(annotations[instance_id].keys()):
                annotation = annotations[instance_id][summarizer_id]
                out.write(annotation)


def save_multiples(multiples: Dict[str, List[PyramidAnnotation]],
                   output_dir: str) -> None:
    with JsonlWriter(f'{output_dir}/task1.d0631.pyramid-annotations.jsonl') as out:
        for summarizer_id in sorted(multiples.keys()):
            for annotation in multiples[summarizer_id]:
                out.write(annotation)


def setup(data_dir: str, output_dir: str):
    pyramid_tar = f'{data_dir}/scrapes/duc.nist.gov/past_duc_aquaint/duc2006/results/Pyramid/DUC2006pyramiddata.tar.gz'
    main(pyramid_tar, output_dir)


def main(pyramid_tar, output_dir):
    pyramids = load_pyramids(pyramid_tar)
    save_pyramids(pyramids, output_dir)

    peer_pyramids, multiples = load_peer_pyramids(pyramid_tar, pyramids)
    save_peer_pyramids(peer_pyramids, output_dir)
    save_multiples(multiples, output_dir)


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('eval_tar')
    argp.add_argument('output_dir')
    args = argp.parse_args()

    main(args.eval_tar, args.output_dir)
