import argparse
import json
import os
import sys
from allennlp.predictors.predictor import Predictor
from allennlp.models.archival import load_archive
from tqdm import tqdm


file_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f'{file_dir}/pytorch-truecaser')

from mylib import *


def main(args):
    archive = load_archive(f'{file_dir}/wiki-truecaser-model-en.tar.gz')
    predictor = Predictor.from_archive(archive, "truecaser-predictor")

    dirname = os.path.dirname(args.output_jsonl)
    if dirname:
        os.makedirs(dirname, exist_ok=True)

    with open(args.output_jsonl, 'w') as out:
        with open(args.input_jsonl, 'r') as f:
            for line in tqdm(f):
                data = json.loads(line)
                text = data['summary']['text']
                if isinstance(text, list):
                    text = ' '.join(text)

                pred = predictor.predict(text)
                truecased_text = predictor.dump_line(pred)
                data['summary']['text'] = truecased_text
                out.write(json.dumps(data) + '\n')


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('--input-jsonl', required=True)
    argp.add_argument('--output-jsonl', required=True)
    args = argp.parse_args()
    main(args)