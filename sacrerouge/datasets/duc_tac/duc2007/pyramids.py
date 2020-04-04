import argparse
import tarfile
from collections import defaultdict
from typing import Dict

from sacrerouge.data import Pyramid, PyramidAnnotation
from sacrerouge.io import JsonlWriter


def load_main_pyramids(main_pyramid_tar: str) -> Dict[str, Pyramid]:
    pyramids = {}
    with tarfile.open(main_pyramid_tar, 'r') as tar:
        for member in tar.getmembers():
            if member.isfile() and member.name.startswith('mainPyramidEval/allpyramids'):
                path = member.name.split('/')
                filename = path[-1]
                parts = filename.split('.')
                instance_id = parts[0].split('-')[0].lower()

                xml = tar.extractfile(member).read().decode()
                pyramid = Pyramid.from_xml(f'{instance_id}', xml, default_document_regex='[-]*\n D[0-9]*\.M\.250\.[A-Z]\.[A-Z]\n[-]*\n')
                pyramids[instance_id] = pyramid

    return pyramids


def load_main_annotations(main_pyramid_tar: str, pyramids: Dict[str, Pyramid]) -> Dict[str, Dict[str, PyramidAnnotation]]:
    annotations = defaultdict(dict)
    with tarfile.open(main_pyramid_tar, 'r') as tar:
        for member in tar.getmembers():
            if member.isfile() and member.name.startswith('mainPyramidEval/allpans'):
                path = member.name.split('/')
                filename = path[-1]
                parts = filename.split('.')
                instance_id = parts[0].lower()
                summarizer_id = parts[4]
                # This directory only has peers
                assert not summarizer_id.isalpha()
                summarizer_type = 'peer'

                pyramid = pyramids[instance_id]
                xml = tar.extractfile(member).read().decode()
                annotation = PyramidAnnotation.from_xml(f'{instance_id}', summarizer_id, summarizer_type, xml, pyramid)
                if annotation:
                    annotations[instance_id][summarizer_id] = annotation
                else:
                    print(f'Annotation for {instance_id}, {summarizer_id} is `None`. Skipping')

    return annotations


def load_update_pyramids(update_tar: str) -> Dict[str, Dict[str, Pyramid]]:
    pyramids = defaultdict(dict)
    with tarfile.open(update_tar, 'r') as tar:
        for member in tar.getmembers():
            if member.isfile() and member.name.startswith('updateEval/Pyramid/allpyramids'):
                path = member.name.split('/')
                filename = path[-1]
                parts = filename.split('-')
                instance_id = parts[0].lower()
                group = parts[1]

                xml = tar.extractfile(member).read().decode()
                pyramid = Pyramid.from_xml(f'{instance_id}-{group}', xml, default_document_regex='[-]*\n D[0-9]*\.M\.250\.[A-Z]\.[A-Z]\n[-]*\n')
                pyramids[instance_id][group] = pyramid

    return pyramids


def load_update_annotations(update_tar: str, pyramids: Dict[str, Dict[str, Pyramid]]) -> Dict[str, Dict[str, Dict[str, PyramidAnnotation]]]:
    annotations = defaultdict(lambda: defaultdict(dict))
    with tarfile.open(update_tar, 'r') as tar:
        for member in tar.getmembers():
            if member.isfile() and member.name.startswith('updateEval/Pyramid/allpans'):
                path = member.name.split('/')
                filename = path[-1]
                parts = filename.split('.')
                instance_id = parts[0].split('-')[0].lower()
                group = parts[0].split('-')[1]
                summarizer_id = parts[4]
                # This directory only has peers
                assert not summarizer_id.isalpha()
                summarizer_type = 'peer'

                pyramid = pyramids[instance_id][group]
                xml = tar.extractfile(member).read().decode()
                annotation = PyramidAnnotation.from_xml(f'{instance_id}-{group}', summarizer_id, summarizer_type, xml, pyramid)
                if annotation:
                    annotations[instance_id][summarizer_id][group] = annotation
                else:
                    print(f'Annotation for {instance_id}-{group}, {summarizer_id} is `None`. Skipping')

    return annotations


def save_main_pyramids(pyramids: Dict[str, Pyramid],
                       output_dir: str) -> None:
    with JsonlWriter(f'{output_dir}/task1.pyramids.jsonl') as out:
        for instance_id in sorted(pyramids.keys()):
            pyramid = pyramids[instance_id]
            out.write(pyramid)


def save_main_pyramid_annotations(annotations: Dict[str, Dict[str, PyramidAnnotation]],
                                  output_dir: str) -> None:
    with JsonlWriter(f'{output_dir}/task1.pyramid-annotations.jsonl') as out:
        for instance_id in sorted(annotations.keys()):
            for summarizer_id in sorted(annotations[instance_id].keys()):
                annotation = annotations[instance_id][summarizer_id]
                out.write(annotation)


def save_update_pyramids(pyramids: Dict[str, Dict[str, Pyramid]],
                         output_dir: str) -> None:
    with JsonlWriter(f'{output_dir}/task2.A.pyramids.jsonl') as out_A:
        with JsonlWriter(f'{output_dir}/task2.B.pyramids.jsonl') as out_B:
            with JsonlWriter(f'{output_dir}/task2.C.pyramids.jsonl') as out_C:
                with JsonlWriter(f'{output_dir}/task2.A-B-C.pyramids.jsonl') as out_A_B_C:
                    for instance_id in sorted(pyramids.keys()):
                        pyramid_A = pyramids[instance_id]['A']
                        pyramid_B = pyramids[instance_id]['B']
                        pyramid_C = pyramids[instance_id]['C']
                        out_A_B_C.write(pyramid_A)
                        out_A_B_C.write(pyramid_B)
                        out_A_B_C.write(pyramid_C)
                        out_A.write(pyramid_A)
                        out_B.write(pyramid_B)
                        out_C.write(pyramid_C)


def save_update_annotations(annotations: Dict[str, Dict[str, Dict[str, PyramidAnnotation]]],
                            output_dir: str) -> None:
    with JsonlWriter(f'{output_dir}/task2.A.pyramid-annotations.jsonl') as out_A:
        with JsonlWriter(f'{output_dir}/task2.B.pyramid-annotations.jsonl') as out_B:
            with JsonlWriter(f'{output_dir}/task2.C.pyramid-annotations.jsonl') as out_C:
                with JsonlWriter(f'{output_dir}/task2.A-B-C.pyramid-annotations.jsonl') as out_A_B_C:
                    for instance_id in sorted(annotations.keys()):
                        for summarizer_id in sorted(annotations[instance_id].keys()):
                            pyramid_A = annotations[instance_id][summarizer_id]['A']
                            out_A_B_C.write(pyramid_A)
                            out_A.write(pyramid_A)

                            pyramid_B = annotations[instance_id][summarizer_id]['B']
                            out_A_B_C.write(pyramid_B)
                            out_B.write(pyramid_B)

                            pyramid_C = annotations[instance_id][summarizer_id]['C']
                            out_A_B_C.write(pyramid_C)
                            out_C.write(pyramid_C)


def setup(data_dir: str, output_dir: str):
    main_pyramid_tar = f'{data_dir}/scrapes/duc.nist.gov/past_duc_aquaint/duc2007/results/mainPyramidEval.tar.gz'
    update_tar = f'{data_dir}/scrapes/duc.nist.gov/past_duc_aquaint/duc2007/results/updateEval.tar.gz'
    main(main_pyramid_tar, update_tar, output_dir)


def main(main_pyramid_tar, update_tar, output_dir):
    main_pyramids = load_main_pyramids(main_pyramid_tar)
    main_pyramid_annotations = load_main_annotations(main_pyramid_tar, main_pyramids)
    save_main_pyramids(main_pyramids, output_dir)
    save_main_pyramid_annotations(main_pyramid_annotations, output_dir)

    update_pyramids = load_update_pyramids(update_tar)
    update_annotations = load_update_annotations(update_tar, update_pyramids)
    save_update_pyramids(update_pyramids, output_dir)
    save_update_annotations(update_annotations, output_dir)


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('main_pyramid_tar')
    argp.add_argument('update_tar')
    argp.add_argument('output_dir')
    args = argp.parse_args()

    main(args.main_pyramid_tar, args.update_tar, args.output_dir)
