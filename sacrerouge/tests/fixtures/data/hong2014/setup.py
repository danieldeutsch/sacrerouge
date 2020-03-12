"""
Sets up the data released in Hong et al. (2014) http://www.cis.upenn.edu/~nlp/corpora/sumrepo/sumrepo_duc2004.tar.gz
for unittesting.
"""
import argparse
import json
import nltk
import os
from glob import glob
from typing import List


def load_one_sentence_per_line_glob(glob_string: str) -> List[List[str]]:
    summaries = []
    for file_path in sorted(glob(glob_string)):
        summary = open(file_path, 'r').read().splitlines()
        summary = list(filter(None, summary))
        summaries.append(summary)
    return summaries


def load_centroid(root_path: str) -> List[List[str]]:
    glob_string = os.path.join(root_path, 'basicsums/Centroid/*.Centroid')
    return load_one_sentence_per_line_glob(glob_string)


def load_freq_sum(root_path: str) -> List[List[str]]:
    glob_string = os.path.join(root_path, 'basicsums/FreqSum/*.FreqSum')
    return load_one_sentence_per_line_glob(glob_string)


def load_greedy_kl(root_path: str) -> List[List[str]]:
    glob_string = os.path.join(root_path, 'basicsums/GreedyKL/*.GreedyKL')
    return load_one_sentence_per_line_glob(glob_string)


def load_lexrank(root_path: str) -> List[List[str]]:
    glob_string = os.path.join(root_path, 'basicsums/LexRank/*.LexRank')
    return load_one_sentence_per_line_glob(glob_string)


def load_ts_sum(root_path: str) -> List[List[str]]:
    glob_string = os.path.join(root_path, 'basicsums/TsSum/*.TsSum')
    return load_one_sentence_per_line_glob(glob_string)


def load_classy04(root_path: str) -> List[List[str]]:
    glob_string = os.path.join(root_path, 'SOAsums/CLASSY04/*.CLASSY04')
    return load_one_sentence_per_line_glob(glob_string)


def load_classy11(root_path: str) -> List[List[str]]:
    glob_string = os.path.join(root_path, 'SOAsums/CLASSY11/*.CLASSY11')
    return load_one_sentence_per_line_glob(glob_string)


def load_dpp(root_path: str) -> List[List[str]]:
    glob_string = os.path.join(root_path, 'SOAsums/DPP/*.DPP')
    summaries = []
    for file_path in sorted(glob(glob_string)):
        summary_text = open(file_path, 'r').read()
        summary = nltk.sent_tokenize(summary_text)
        summaries.append(summary)
    return summaries


def load_icsi_summ(root_path: str) -> List[List[str]]:
    glob_string = os.path.join(root_path, 'SOAsums/ICSISumm/*.ICSISumm')
    return load_one_sentence_per_line_glob(glob_string)


def load_occams_v(root_path: str) -> List[List[str]]:
    glob_string = os.path.join(root_path, 'SOAsums/OCCAMS_V/*.OCCAMS_V')
    return load_one_sentence_per_line_glob(glob_string)


def load_reg_sum(root_path: str) -> List[List[str]]:
    glob_string = os.path.join(root_path, 'SOAsums/RegSum/*.RegSum')
    return load_one_sentence_per_line_glob(glob_string)


def load_submodular(root_path: str) -> List[List[str]]:
    glob_string = os.path.join(root_path, 'SOAsums/Submodular/*.Submodular')
    return load_one_sentence_per_line_glob(glob_string)


def save_summaries(summaries: List[List[str]], file_path: str) -> None:
    output_dir = os.path.dirname(file_path)
    os.makedirs(output_dir, exist_ok=True)
    with open(file_path, 'w') as out:
        for summary in summaries:
            output_data = {'summary': summary}
            out.write(json.dumps(output_data) + '\n')


def main(args):
    centroid = load_centroid(args.hong2014_root)
    freq_sum = load_freq_sum(args.hong2014_root)
    greedy_kl = load_greedy_kl(args.hong2014_root)
    lexrank = load_lexrank(args.hong2014_root)
    ts_sum = load_ts_sum(args.hong2014_root)
    classy04 = load_classy04(args.hong2014_root)
    classy11 = load_classy11(args.hong2014_root)
    dpp = load_dpp(args.hong2014_root)
    icsi_summ = load_icsi_summ(args.hong2014_root)
    occams_v = load_occams_v(args.hong2014_root)
    reg_sum = load_reg_sum(args.hong2014_root)
    submodular = load_submodular(args.hong2014_root)

    save_summaries(centroid, os.path.join(args.output_root, 'centroid.jsonl'))
    save_summaries(freq_sum, os.path.join(args.output_root, 'freq-sum.jsonl'))
    save_summaries(greedy_kl, os.path.join(args.output_root, 'greedy-kl.jsonl'))
    save_summaries(lexrank, os.path.join(args.output_root, 'lexrank.jsonl'))
    save_summaries(ts_sum, os.path.join(args.output_root, 'ts-sum.jsonl'))
    save_summaries(classy04, os.path.join(args.output_root, 'classy04.jsonl'))
    save_summaries(classy11, os.path.join(args.output_root, 'classy11.jsonl'))
    save_summaries(dpp, os.path.join(args.output_root, 'dpp.jsonl'))
    save_summaries(icsi_summ, os.path.join(args.output_root, 'icsi-summ.jsonl'))
    save_summaries(occams_v, os.path.join(args.output_root, 'occams-v.jsonl'))
    save_summaries(reg_sum, os.path.join(args.output_root, 'reg-sum.jsonl'))
    save_summaries(submodular, os.path.join(args.output_root, 'submodular.jsonl'))


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('hong2014_root',
                      help='The path to the untarred root directory of the data released '
                           'by Hong et al. 2014 (http://www.cis.upenn.edu/~nlp/corpora/sumrepo/sumrepo_duc2004.tar.gz).')
    argp.add_argument('output_root',
                      help='The path to the root of the directory where the summaries should be saved.')
    args = argp.parse_args()
    main(args)
