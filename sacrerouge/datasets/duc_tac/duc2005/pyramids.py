import tarfile
from collections import defaultdict
from typing import Dict, List

from sacrerouge.data import Pyramid, PyramidAnnotation
from sacrerouge.io import JsonlWriter


def load_pyramids(pyramid_tar: str) -> Dict[str, Pyramid]:
    pyramids = {}
    with tarfile.open(pyramid_tar, 'r') as tar:
        for member in tar.getmembers():
            if member.isfile() and member.name.startswith('pans/'):
                path = member.name.split('/')
                filename = path[-1]
                instance_id = filename.split('.')[1].lower()

                # For this dataset, the pyramid and annotations are all in the same file, one per
                # annotation. Therefore, we only need to load the pyramid once from the first file
                if instance_id in pyramids:
                    continue

                xml = tar.extractfile(member).read().decode()
                pyramid = Pyramid.from_xml(instance_id, xml,
                                           default_document_regex='[-]*\n(\s*)D[0-9]*\.M\.250\.[A-Z]\.[A-Z]\n[-]*\n',
                                           is_combined_file=True)
                pyramids[instance_id] = pyramid

    return pyramids


def load_peer_pyramids(eval_tar: str, pyramids: Dict[str, Pyramid]) -> Dict[str, Dict[str, PyramidAnnotation]]:
    annotations = defaultdict(dict)
    with tarfile.open(eval_tar, 'r') as tar:
        for member in tar.getmembers():
            if member.isfile() and member.name.startswith('pans/'):
                path = member.name.split('/')
                filename = path[-1]
                parts = filename.split('.')
                instance_id = parts[1].lower()
                summarizer_id = parts[5]

                if summarizer_id.isalpha():
                    summarizer_type = 'reference'
                else:
                    summarizer_type = 'peer'

                pyramid = pyramids[instance_id]
                xml = tar.extractfile(member).read().decode()
                annotation = PyramidAnnotation.from_xml(f'{instance_id}', summarizer_id, summarizer_type, xml, pyramid)
                if annotation:
                    annotations[instance_id][summarizer_id] = annotation
                else:
                    print(f'Annotation for {instance_id}, {summarizer_id} is `None`. Skipping')

    return annotations


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


def setup(data_dir: str, output_dir: str):
    pyramid_tar = f'{data_dir}/scrapes/duc.nist.gov/past_duc/duc2005/results/Pyramid/DUC2005.tar.gz'
    main(pyramid_tar, output_dir)


def main(pyramid_tar, output_dir):
    pyramids = load_pyramids(pyramid_tar)
    save_pyramids(pyramids, output_dir)

    peer_pyramids = load_peer_pyramids(pyramid_tar, pyramids)
    save_peer_pyramids(peer_pyramids, output_dir)

