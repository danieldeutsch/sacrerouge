import tarfile
from io import BytesIO
from lxml import etree
from tqdm import tqdm
from typing import Dict, List

from sacrerouge.common.util import download_url_to_file
from sacrerouge.io import JsonlWriter


def _extract_data(xml_bytes: bytes) -> Dict:
    root = etree.parse(BytesIO(xml_bytes))

    try:
        doc_id = root.xpath('./head/docdata/doc-id')[0].get('id-string')

        year = root.xpath('./head/meta[@name="publication_year"]')[0].get('content')
        month = root.xpath('./head/meta[@name="publication_month"]')[0].get('content')
        day = root.xpath('./head/meta[@name="publication_day_of_month"]')[0].get('content')

        # We prefer hl1, but fallback to hl2 if it does not exist
        nodes = root.xpath('./body/body.head/hedline/hl1')
        if len(nodes) == 0:
            nodes = root.xpath('./body/body.head/hedline/hl2')
        headline = nodes[0].text.strip()
        assert len(headline) > 0

        abstract = []
        for node in root.xpath('./body/body.head/abstract/p'):
            text = node.text.strip()
            if text:
                abstract.append(text)
        assert len(abstract) == 1
        abstract = abstract[0]

        document = []
        for node in root.xpath('./body/body.content/block[@class="full_text"]/p'):
            text = node.text.strip()
            if text:
                document.append(text)
        assert len(document) > 0

        return {
            'instance_id': doc_id,
            'document': {
                'date': f'{year}-{month}-{day}',
                'headline': headline,
                'text': document,
            },
            'summary': {
                'text': abstract
            }
        }
    except:
        print(xml_bytes.decode())


def _save(instances: List, file_path: str) -> None:
    with JsonlWriter(file_path) as out:
        for instance in instances:
            out.write(instance)


def setup(ldc2008t19_tgz: str, output_dir: str, force: bool) -> None:
    # Download the splits from https://github.com/jiacheng-xu/DiscoBERT/tree/release/data_preparation/urls_nyt
    for split in ['train', 'valid', 'test']:
        download_url_to_file(f'https://github.com/jiacheng-xu/DiscoBERT/raw/release/data_preparation/urls_nyt/mapping_{split}.txt',
                             f'{output_dir}/raw/mapping_{split}.txt',
                             force=force)

    train_ids = set(map(int, open(f'{output_dir}/raw/mapping_train.txt', 'r').read().splitlines()))
    valid_ids = set(map(int, open(f'{output_dir}/raw/mapping_valid.txt', 'r').read().splitlines()))
    test_ids = set(map(int, open(f'{output_dir}/raw/mapping_test.txt', 'r').read().splitlines()))
    all_ids = train_ids | valid_ids | test_ids

    train, valid, test = [], [], []
    with tarfile.open(ldc2008t19_tgz, 'r') as tar:
        # Obtain the members to make the tqdm output make sense
        members = []
        for member in tar.getmembers():
            if not member.name.startswith('nyt_corpus/data') or not member.name.endswith('.tgz'):
                continue
            members.append(member)

        for member in tqdm(members):
            tar_bytes = tar.extractfile(member).read()
            with tarfile.open(fileobj=BytesIO(tar_bytes)) as inner_tar:
                for inner_member in inner_tar.getmembers():
                    if not inner_member.name.endswith('.xml'):
                        continue

                    # "01/26/1459527.xml"
                    file_id = int(inner_member.name.split('/')[-1][:-4])
                    if file_id in all_ids:
                        xml_bytes = inner_tar.extractfile(inner_member).read()
                        instance = _extract_data(xml_bytes)

                        if file_id in train_ids:
                            train.append(instance)
                        elif file_id in valid_ids:
                            valid.append(instance)
                        elif file_id in test_ids:
                            test.append(instance)

    assert len(train) == 137778, f'Train has {len(train)} instances, expected 137778'
    assert len(valid) == 17222, f'Valid has {len(valid)} instances, expected 17222'
    assert len(test) == 17223, f'Test has {len(test)} instances, expected 17223'

    _save(train, f'{output_dir}/train.jsonl.gz')
    _save(valid, f'{output_dir}/valid.jsonl.gz')
    _save(test, f'{output_dir}/test.jsonl.gz')