from collections import Counter
from typing import Dict, List, Tuple

from sacrerouge.common.util import download_file_from_google_drive, download_url_to_file
from sacrerouge.io import JsonlWriter


def _download_documents_and_summaries(output_dir: str, force: bool) -> None:
    # The source files come from the "Raw data, bad retrievals removed" link on https://github.com/Alex-Fabbri/Multi-News
    download_file_from_google_drive('1wHAWDOwOoQWSj7HYpyJ3Aeud8WhhaJ7P', f'{output_dir}/train.src.cleaned', force=force)
    download_file_from_google_drive('1p_u9_jpz3Zbj0EL05QFX6wvJAahmOn6h', f'{output_dir}/val.src.cleaned', force=force)
    download_file_from_google_drive('1-n_6fj-1nM7sWtBSNkQCSfl5Rb3zPVfr', f'{output_dir}/test.src.cleaned', force=force)

    # The target files come from the "Raw data" link
    download_file_from_google_drive('1QVgswwhVTkd3VLCzajK6eVkcrSWEK6kq', f'{output_dir}/train.tgt', force=force)
    download_file_from_google_drive('1Y1lBbBU5Q0aJMqLhYEOdEtTqQ85XnRRM', f'{output_dir}/val.tgt', force=force)
    download_file_from_google_drive('1CX_YcgQ3WwNC1fXBpMfwMXFPCqsd9Lbp', f'{output_dir}/test.tgt', force=force)


def _download_ids(output_dir: str, force: bool) -> None:
    download_url_to_file('https://raw.githubusercontent.com/Alex-Fabbri/Multi-News/master/data/ids/train.id', f'{output_dir}/train.id', force=force)
    download_url_to_file('https://raw.githubusercontent.com/Alex-Fabbri/Multi-News/master/data/ids/val.id', f'{output_dir}/val.id', force=force)
    download_url_to_file('https://raw.githubusercontent.com/Alex-Fabbri/Multi-News/master/data/ids/test.id', f'{output_dir}/test.id', force=force)


def _load_ids(input_file: str) -> List[str]:
    return open(input_file, 'r').read().splitlines()


def _load_documents(input_file: str) -> Tuple[List[List[Dict]], int]:
    documents_list = []
    num_empty = 0
    with open(input_file, 'r') as f:
        for line in f:
            raw_documents = line.strip().split('|||||')
            documents = []
            for raw in raw_documents:
                text = raw.split('NEWLINE_CHAR')
                text = [s.strip() for s in text if len(s.strip()) > 0]
                if len(text) > 0:
                    documents.append({'text': text})
                else:
                    num_empty += 1
            documents_list.append(documents)
    return documents_list, num_empty


def _load_summaries(input_file: str) -> List[Dict]:
    summaries = []
    with open(input_file, 'r') as f:
        for line in f:
            if line.startswith('-'):
                line = line[1:]
            line = line.strip()
            assert len(line) > 0
            summaries.append({'text': line})
    return summaries


def _combine(documents_list: List[List[Dict]], summaries: List[Dict], ids: List[str]) -> List:
    assert len(documents_list) == len(summaries) == len(ids)
    instances = []
    for instance_id, documents, summary in zip(ids, documents_list, summaries):
        instances.append({
            'instance_id': instance_id,
            'documents': documents,
            'summary': summary
        })
    return instances


def _get_stats(instances: List) -> Counter:
    counts = Counter()
    for instance in instances:
        counts[len(instance['documents'])] += 1
    return counts


def _filter_to_having_source_documents(instances: List) -> List:
    filtered = []
    for instance in instances:
        if len(instance['documents']) > 0:
            filtered.append(instance)
    return filtered


def _filter_to_multidoc(instances: List) -> List:
    filtered = []
    for instance in instances:
        if len(instance['documents']) > 1:
            filtered.append(instance)
    return filtered


def _save(instances: List, output_file: str) -> None:
    with JsonlWriter(output_file) as out:
        for instance in instances:
            out.write(instance)


def setup(output_dir: str, force: bool) -> None:
    _download_documents_and_summaries(f'{output_dir}/raw', force)
    _download_ids(f'{output_dir}/raw', force)

    train_ids = _load_ids(f'{output_dir}/raw/train.id')
    valid_ids = _load_ids(f'{output_dir}/raw/val.id')
    test_ids = _load_ids(f'{output_dir}/raw/test.id')

    train_documents, train_empty = _load_documents(f'{output_dir}/raw/train.src.cleaned')
    valid_documents, valid_empty = _load_documents(f'{output_dir}/raw/val.src.cleaned')
    test_documents, test_empty = _load_documents(f'{output_dir}/raw/test.src.cleaned')

    train_summaries = _load_summaries(f'{output_dir}/raw/train.tgt')
    valid_summaries = _load_summaries(f'{output_dir}/raw/val.tgt')
    test_summaries = _load_summaries(f'{output_dir}/raw/test.tgt')

    train = _combine(train_documents, train_summaries, train_ids)
    valid = _combine(valid_documents, valid_summaries, valid_ids)
    test = _combine(test_documents, test_summaries, test_ids)

    print('Number of documents with no text')
    print('Train', train_empty)
    print('Valid', valid_empty)
    print('Test', test_empty)
    print()

    train_stats = _get_stats(train)
    valid_stats = _get_stats(valid)
    test_stats = _get_stats(test)

    train_total = sum(train_stats.values())
    valid_total = sum(valid_stats.values())
    test_total = sum(test_stats.values())

    print('Number of source document counts')
    print('Train', train_stats, train_total)
    print('Valid', valid_stats, valid_total)
    print('Test', test_stats, test_total)
    print()

    train = _filter_to_having_source_documents(train)
    valid = _filter_to_having_source_documents(valid)
    test = _filter_to_having_source_documents(test)

    train_stats = _get_stats(train)
    valid_stats = _get_stats(valid)
    test_stats = _get_stats(test)

    train_total = sum(train_stats.values())
    valid_total = sum(valid_stats.values())
    test_total = sum(test_stats.values())

    print('Number of source document counts (after removing instances with 0 source documents)')
    print('Train', train_stats, train_total)
    print('Valid', valid_stats, valid_total)
    print('Test', test_stats, test_total)
    print()

    _save(train, f'{output_dir}/train.jsonl.gz')
    _save(valid, f'{output_dir}/valid.jsonl.gz')
    _save(test, f'{output_dir}/test.jsonl.gz')

    train_multi = _filter_to_multidoc(train)
    valid_multi = _filter_to_multidoc(valid)
    test_multi = _filter_to_multidoc(test)

    train_stats = _get_stats(train_multi)
    valid_stats = _get_stats(valid_multi)
    test_stats = _get_stats(test_multi)

    train_total = sum(train_stats.values())
    valid_total = sum(valid_stats.values())
    test_total = sum(test_stats.values())

    print('Number of source document counts (after removing instances with 1 source document)')
    print('Train', train_stats, train_total)
    print('Valid', valid_stats, valid_total)
    print('Test', test_stats, test_total)
    print()

    _save(train_multi, f'{output_dir}/train.multi.jsonl.gz')
    _save(valid_multi, f'{output_dir}/valid.multi.jsonl.gz')
    _save(test_multi, f'{output_dir}/test.multi.jsonl.gz')

