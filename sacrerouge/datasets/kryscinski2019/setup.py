import os
import tarfile
from typing import List, Tuple

from sacrerouge.common.util import download_file_from_google_drive, download_url_to_file
from sacrerouge.io import JsonlReader, JsonlWriter


def _download_data(output_dir: str, force: bool) -> Tuple[str, str, str]:
    # Download the CNN stories tar
    cnn_tar = f"{output_dir}/cnn_stories.tgz"
    download_file_from_google_drive("0BwmD_VLjROrfTHk4NFg2SndKcjQ", cnn_tar, force=force)

    # Download the Dailymail stories tar
    dailymail_tar = f"{output_dir}/dailymail_stories.tgz"
    download_file_from_google_drive("0BwmD_VLjROrfM1BxdkxVaTY2bWs", dailymail_tar, force=force)

    # Download the annotationed validation and testing data
    valid_test_tar = f"{output_dir}/unpaired_annotated_data.tar.gz"
    download_url_to_file("https://storage.googleapis.com/sfr-factcc-data-research/unpaired_annotated_data.tar.gz",
                         valid_test_tar,
                         force=force)

    return cnn_tar, dailymail_tar, valid_test_tar


def _untar(tar_path: str, output_dir: str) -> None:
    with tarfile.open(tar_path, "r") as tar:
        tar.extractall(output_dir)


def parse_story_file(content):
    """
    Remove article highlights and unnecessary white characters.
    """
    content_raw = content.split("@highlight")[0]
    content = " ".join(filter(None, [x.strip() for x in content_raw.split("\n")]))
    return content


def _load_instances(input_file: str, cnn_dir: str, dailymail_dir: str) -> List:
    instances = []
    with JsonlReader(input_file) as f:
        for instance in f:
            # Remove "cnndm/"
            filepath = instance["filepath"][6:]
            if filepath.startswith("cnn"):
                content = open(f"{cnn_dir}/{filepath[4:]}", "r").read()
            else:
                content = open(f"{dailymail_dir}/{filepath[10:]}", "r").read()
            document = parse_story_file(content)

            instances.append({
                "instance_id": instance["id"],
                "filepath": instance["filepath"],
                "summarizer_id": "kryscinski2019",
                "summarizer_type": "peer",
                "document": {"text": document},
                "summary": {"text": instance["claim"]},
                "label": instance["label"],
            })

    return instances


def _save_data(items: List, output_file: str) -> None:
    with JsonlWriter(output_file) as out:
        for item in items:
            out.write(item)


def setup(output_dir: str, force: bool) -> None:
    raw_dir = f"{output_dir}/raw"
    cnn_tar, dailymail_tar, valid_test_tar = _download_data(raw_dir, force)

    cnn_dir = f"{output_dir}/raw/cnn"
    if not os.path.exists(cnn_dir) or force:
        _untar(cnn_tar, raw_dir)

    dailymail_dir = f"{output_dir}/raw/dailymail"
    if not os.path.exists(dailymail_dir) or force:
        _untar(dailymail_tar, raw_dir)

    valid_test_dir = f"{output_dir}/raw/unpaired_annotated_data"
    if not os.path.exists(valid_test_dir) or force:
        _untar(valid_test_tar, raw_dir)

    valid = _load_instances(
        f"{valid_test_dir}/val/data-dev.jsonl",
        cnn_dir,
        dailymail_dir
    )
    test = _load_instances(
        f"{valid_test_dir}/test/data-dev.jsonl",
        cnn_dir,
        dailymail_dir
    )
    _save_data(valid, f"{output_dir}/valid.jsonl")
    _save_data(test, f"{output_dir}/test.jsonl")