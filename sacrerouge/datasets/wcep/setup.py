from typing import List

from sacrerouge.common.util import download_file_from_google_drive
from sacrerouge.io import JsonlReader, JsonlWriter


def _download_data(output_dir: str, force: bool) -> None:
    download_file_from_google_drive('1kUjSRXzKnTYdJ732BkKVLg3CFxDKo25u', f'{output_dir}/train.jsonl.gz', force=force)
    download_file_from_google_drive('1_kHTZ32jazTbXaFRg0vBeIsVcpI7CTmy', f'{output_dir}/val.jsonl.gz', force=force)
    download_file_from_google_drive('1qsd5pOCpeSXsaqNobXCrcAzhcjtG1wA1', f'{output_dir}/test.jsonl.gz', force=force)


def _load_instances(input_file: str) -> List:
    instances = []
    with JsonlReader(input_file) as f:
        for instance in f:
            instance_id = str(instance['id'])
            date = instance['date']
            reference_urls = set(instance['reference_urls'])
            summary = instance['summary']
            documents = []
            for article in instance['articles']:
                document_id = article['id']
                title = article['title']
                text = article['text']
                url = article['url']
                origin = article['origin']
                time = article['time']

                if origin == 'WCEP':
                    assert url in reference_urls

                documents.append({
                    'document_id': document_id,
                    'title': title,
                    'url': url,
                    'time': time,
                    'origin': origin,
                    'text': text
                })
            assert len(documents) > 0

            instances.append({
                'instance_id': instance_id,
                'date': date,
                'documents': documents,
                'summary': {'text': summary}
            })
    return instances


def _count_num_documents(instances: List) -> int:
    return sum(len(instance['documents']) for instance in instances)


def _remove_duplicates(instances: List) -> int:
    num_removed = 0
    for instance in instances:
        url_to_origin = {}
        url_to_document = {}
        for document in instance['documents']:
            url = document['url']
            origin = document['origin']
            if url in url_to_origin:
                if origin == 'WCEP' and url_to_origin[url] != 'WCEP':
                    # We prefer the WCEP url not the CommonCrawl url
                    url_to_origin[url] = origin
                    url_to_document[url] = document
                else:
                    # Otherwise, we just leave what is already there
                    pass
                # This is a duplicate, whether we removed the one we already
                # found or this one
                num_removed += 1
            else:
                url_to_origin[url] = origin
                url_to_document[url] = document

        instance['documents'] = list(url_to_document.values())
    return num_removed


def _save(instances: List, output_file: str) -> None:
    with JsonlWriter(output_file) as out:
        for instance in instances:
            out.write(instance)


def setup(output_dir: str, force: bool) -> None:
    _download_data(f'{output_dir}/raw', force)

    train = _load_instances(f'{output_dir}/raw/train.jsonl.gz')
    valid = _load_instances(f'{output_dir}/raw/val.jsonl.gz')
    test = _load_instances(f'{output_dir}/raw/test.jsonl.gz')

    train_num_duplicates = _remove_duplicates(train)
    valid_num_duplicates = _remove_duplicates(valid)
    test_num_duplicates = _remove_duplicates(test)

    print('Number of duplicate source documents removed')
    print('Train', train_num_duplicates)
    print('Valid', valid_num_duplicates)
    print('Test', test_num_duplicates)

    _save(train, f'{output_dir}/train.jsonl.gz')
    _save(valid, f'{output_dir}/valid.jsonl.gz')
    _save(test, f'{output_dir}/test.jsonl.gz')


