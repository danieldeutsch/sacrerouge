import argparse
import tarfile
from collections import defaultdict
from typing import Dict

from sacrerouge.data import Pyramid
from sacrerouge.io import JsonlWriter


def load_pyramids(eval_tar: str) -> Dict[str, Dict[str, Pyramid]]:
    pyramids = defaultdict(dict)
    with tarfile.open(eval_tar, 'r') as tar:
        for member in tar.getmembers():
            if member.isfile() and member.name.startswith('UpdateSumm08_eval/manual/pyramids'):
                path = member.name.split('/')
                filename = path[-1]
                parts = filename.split('.')
                instance_id = parts[0].split('-')[0].lower()
                group = parts[0].split('-')[1]

                xml = tar.extractfile(member).read().decode()
                pyramid = Pyramid.from_xml(f'{instance_id}-{group}', xml)
                pyramids[instance_id][group] = pyramid

    return pyramids


def save_pyramids(pyramids: Dict[str, Dict[str, Pyramid]],
                  output_dir: str) -> None:
    with JsonlWriter(f'{output_dir}/task1.A.pyramids.jsonl') as out_A:
        with JsonlWriter(f'{output_dir}/task1.B.pyramids.jsonl') as out_B:
            with JsonlWriter(f'{output_dir}/task1.A-B.pyramids.jsonl') as out_A_B:
                for instance_id in sorted(pyramids.keys()):
                    pyramid_A = pyramids[instance_id]['A']
                    pyramid_B = pyramids[instance_id]['B']
                    out_A_B.write(pyramid_A)
                    out_A_B.write(pyramid_B)
                    out_A.write(pyramid_A)
                    out_B.write(pyramid_B)


def setup(data_dir: str, output_dir: str):
    eval_tar = f'{data_dir}/scrapes/tac.nist.gov/protected/past-aquaint2/2008/UpdateSumm08_eval.tar.gz'
    main(eval_tar, output_dir)


def main(eval_tar, output_dir):
    pyramids = load_pyramids(eval_tar)
    save_pyramids(pyramids, output_dir)


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('eval_tar')
    argp.add_argument('output_dir')
    args = argp.parse_args()

    main(args.eval_tar, args.output_dir)
