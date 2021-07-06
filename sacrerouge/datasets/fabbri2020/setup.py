import json
import os
import shutil
import tarfile
from collections import Counter
from typing import Any, Dict, List, Tuple

from sacrerouge.common.util import download_file_from_google_drive, download_url_to_file
from sacrerouge.data import Metrics, MetricsDict
from sacrerouge.datasets.fabbri2020.pair_data import run_pair_data, parse_story_file
from sacrerouge.io import JsonlReader, JsonlWriter


def download_tars(output_dir: str, force: bool) -> Tuple[str, str]:
    # Downloads the "story" tarfiles from https://cs.nyu.edu/~kcho/DMQA/
    cnn_tar = f'{output_dir}/cnn_stories.tgz'
    dailymail_tar = f'{output_dir}/dailymail_stories.tgz'
    download_file_from_google_drive('0BwmD_VLjROrfTHk4NFg2SndKcjQ', cnn_tar, force=force)
    download_file_from_google_drive('0BwmD_VLjROrfM1BxdkxVaTY2bWs', dailymail_tar, force=force)
    return cnn_tar, dailymail_tar


def download_human_judgments(output_dir: str, force: bool) -> str:
    url = 'https://storage.googleapis.com/sfr-summarization-repo-research/model_annotations.aligned.jsonl'
    file_path = f'{output_dir}/model_annotations.aligned.jsonl'
    download_url_to_file(url, file_path, force)
    return file_path


def download_system_outputs(output_dir: str, force: bool) -> str:
    expanded_dir = f'{output_dir}/expanded/'
    for system_id in range(0, 24):
        url = f'https://storage.googleapis.com/sfr-summarization-repo-research/M{system_id}.tar.gz'
        file_path = f'{output_dir}/M{system_id}.tar.gz'
        download_url_to_file(url, file_path, force)

        model_expanded_dir = f'{expanded_dir}/M{system_id}'
        if os.path.exists(model_expanded_dir) and force:
            shutil.rmtree(model_expanded_dir)

        if not os.path.exists(model_expanded_dir):
            with tarfile.open(file_path, 'r') as tar:
                tar.extractall(expanded_dir)
    return expanded_dir


def load_judgments(file_path: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Metrics]]:
    summaries = []
    summaries_with_crowd = []
    metrics_list = []

    with JsonlReader(file_path) as f:
        for instance in f:
            instance_id = instance['id']
            summarizer_id = instance['model_id']
            filename = instance['filepath']
            summary = {'text': instance['decoded']}
            references = instance['references']
            expert_annotations = instance['expert_annotations']
            turker_annotations = instance['turker_annotations']
            document = instance['text']

            # The first reference is always the ground-truth
            # https://github.com/Yale-LILY/SummEval/issues/8
            assert len(references) == 11
            references[0] = {
                'summarizer_id': 'ground-truth',
                'summarizer_type': 'reference',
                'text': references[0]
            }
            for i in range(1, 11):
                references[i] = {
                    'summarizer_id': f'turker-{i}',
                    'summarizer_type': 'reference',
                    'text': references[i]
                }

            summaries.append({
                'instance_id': instance_id,
                'summarizer_id': summarizer_id,
                'summarizer_type': 'peer',
                'file_path': filename,
                'document': {'text': document},
                'summary': summary,
                'references': [references[0]]
            })
            summaries_with_crowd.append({
                'instance_id': instance_id,
                'summarizer_id': summarizer_id,
                'summarizer_type': 'peer',
                'file_path': filename,
                'document': {'text': document},
                'summary': summary,
                'references': references
            })

            expert_metrics = MetricsDict({
                'coherence': [annotation['coherence'] for annotation in expert_annotations],
                'consistency': [annotation['consistency'] for annotation in expert_annotations],
                'fluency': [annotation['fluency'] for annotation in expert_annotations],
                'relevance': [annotation['relevance'] for annotation in expert_annotations]
            })
            turker_metrics = MetricsDict({
                'coherence': [annotation['coherence'] for annotation in turker_annotations],
                'consistency': [annotation['consistency'] for annotation in turker_annotations],
                'fluency': [annotation['fluency'] for annotation in turker_annotations],
                'relevance': [annotation['relevance'] for annotation in turker_annotations]
            })
            both = MetricsDict({
                'expert': expert_metrics,
                'turker': turker_metrics
            })
            metrics = Metrics(instance_id, summarizer_id, 'peer', both)
            metrics_list.append(metrics)

    return summaries, summaries_with_crowd, metrics_list


def setup_documents(cnn_tar: str, dailymail_tar: str, output_dir: str, force: bool) -> None:
    cnn_dir = f'{output_dir}/raw/cnndm/cnn'
    dm_dir = f'{output_dir}/raw/cnndm/dailymail'
    for tar_path, target_path in [(cnn_tar, cnn_dir), (dailymail_tar, dm_dir)]:
        if os.path.exists(target_path) and force:
            print(f'Removing {target_path}')
            shutil.rmtree(target_path)

        if not os.path.exists(target_path):
            print(f'Untarring {tar_path} (it\'s pretty slow...)')
            with tarfile.open(tar_path, 'r') as tar:
                tar.extractall(f'{output_dir}/raw/cnndm')


def load_system_outputs(dirname: str, judged_summaries: List, documents_root: str) -> List:
    # Some of the output directories have multiple outputs, likely from different
    # versions of the models. This mapping marks which of those output files was
    # used in the annotations
    # https://github.com/Yale-LILY/SummEval/issues/8
    model_to_filename = {
        'M0': 'outputs.aligned.jsonl',
        'M1': 'outputs.aligned.jsonl',
        'M2': 'outputs.aligned.jsonl',
        'M5': 'outputs_rouge.aligned.jsonl',
        'M8': 'outputs_ptrgen+cov.aligned.jsonl',
        'M9': 'outputs_extabs+rl+rerank.aligned.jsonl',
        'M10': 'outputs_encdec.aligned.jsonl',
        'M11': 'outputs_novelty.aligned.jsonl',
        'M12': 'outputs.aligned.jsonl',
        'M13': 'outputs.aligned.jsonl',
        'M14': 'outputs.aligned.jsonl',
        'M15': 'outputs_coverage.aligned.jsonl',
        'M17': 'outputs_11B.aligned.jsonl',
        'M20': 'outputs_zeroshot.aligned.jsonl',
        'M22': 'outputs_cnndm.aligned.jsonl',
        'M23': 'outputs_c4_cnn_dailymail.aligned.jsonl',
    }

    document_cache = {}
    outputs = []

    # The model outputs can have duplicate IDs if the instances were mapped
    # to the same inputs. We only keep the first occurrence of any duplicate.
    # However, dm-test-2c37d44d03ce2e91310339d884d33ee5aabf9abc is duplicated and selected
    # to be judged. We want to ensure that the summary saved here is the one which
    # was judged, so we need to keep track of that information.
    seen = set()
    seen_and_judged = set()
    judged = {}
    for instance in judged_summaries:
        instance_id = instance['instance_id']
        summarizer_id = instance['summarizer_id']
        summary = instance['summary']['text']
        judged[(instance_id, summarizer_id)] = summary

    for summarizer_id, filename in sorted(model_to_filename.items()):
        file_path = f'{dirname}/{summarizer_id}/aligned/{filename}'
        print(f'Processing {file_path}')
        instances = JsonlReader(file_path).read()
        for instance in instances:
            instance_id = instance['id']

            # For some reason, there is an example with the filepath as the ID. The rest are not like this
            if instance_id == 'cnndm/dailymail/stories/cbed2a778a5e17d729c6e5ee5691b88710620dd7.story':
                instance_id = 'dm-test-cbed2a778a5e17d729c6e5ee5691b88710620dd7'

            # This json is messed up somehow, but you can see the decoded summary is empty
            if summarizer_id == 'M2' and instance_id == 'dm-test-9f270039c861e75ee2f01e4e2898a9ea04a96b26':
                summary = ''
            else:
                summary = instance['decoded']

            is_judged = (instance_id, summarizer_id) in judged
            if is_judged:
                judged_summary = judged[(instance_id, summarizer_id)]

                # This pair has a weird encoding which causes the summaries to not be equal.
                # It's not a duplicate instance, so we just take it
                if summarizer_id == 'M23' and instance_id == 'dm-test-2cf8c2d1d2ceb1980249f77e703f9039e63799d0':
                    summary = judged_summary

                if summary != judged_summary:
                    # We do not want this one
                    continue

            if (instance_id, summarizer_id) in seen:
                # We only want the first one
                continue
            seen.add((instance_id, summarizer_id))
            if is_judged:
                seen_and_judged.add((instance_id, summarizer_id))

            filepath = instance['filepath']
            if filepath not in document_cache:
                with open(f'{documents_root}/{filepath}', 'r') as f:
                    story_content = f.read()
                    document_cache[filepath] = parse_story_file(story_content)
            document = document_cache[filepath]

            reference = instance['reference']
            outputs.append({
                'instance_id': instance_id,
                'summarizer_id': summarizer_id,
                'summarizer_type': 'peer',
                'filepath': filepath,
                'document': {'text': document},
                'summary': {'text': summary},
                'reference': {'text': reference}
            })

    # Ensure that we saved all of the summaries that were judged
    assert seen_and_judged == set(judged.keys())

    return outputs


def ensure_no_duplicates(items: List) -> None:
    seen = set()
    for item in items:
        instance_id = item['instance_id']
        summarizer_id = item['summarizer_id']
        key = (instance_id, summarizer_id)
        assert key not in seen
        seen.add(key)


def sanity_check(judged_summaries: List, all_summaries: List, metrics_list: List[Metrics]) -> None:
    ensure_no_duplicates(judged_summaries)
    ensure_no_duplicates(all_summaries)

    judged_summaries = {
        (instance['instance_id'], instance['summarizer_id']): instance
        for instance in judged_summaries
    }
    all_summaries = {
        (instance['instance_id'], instance['summarizer_id']): instance
        for instance in all_summaries
    }
    metrics_dict = set([(instance.instance_id, instance.summarizer_id) for instance in metrics_list])

    # Ensure no duplicate metrics
    assert len(metrics_list) == len(metrics_list)

    # Ensure all judged are in all_summaries and metrics_dict
    assert len(judged_summaries) == len(metrics_dict)
    for key in judged_summaries.keys():
        assert key in all_summaries
        assert key in metrics_dict

        # Make sure the summaries are identical
        summary = all_summaries[key]['summary']['text']
        judged_summary = judged_summaries[key]['summary']['text']
        assert summary == judged_summary

        # Make sure the documents are identical
        document = all_summaries[key]['document']['text']
        judged_document = judged_summaries[key]['document']['text']
        assert document == judged_document

        # We do not check the references because they are different. The references
        # in all_summaries seem be normalized, whereas the summaries in judged_summaries
        # are not.
        # reference = all_summaries[key]['reference']['text']
        # judged_reference = judged_summaries[key]['references'][0]['text']
        # assert reference == judged_reference, key


def print_stats(summaries: List):
    summarizer_ids = Counter()
    instance_ids = Counter()

    for instance in summaries:
        instance_id = instance['instance_id']
        summarizer_id = instance['summarizer_id']
        summarizer_ids[summarizer_id] += 1
        instance_ids[instance_id] += 1

    print('Num instances per summarizer')
    print(json.dumps(summarizer_ids, indent=2))

    max_count = max(instance_ids.values())
    missing_summaries = {}
    for instance_id, count in instance_ids.items():
        if count != max_count:
            missing_summaries[instance_id] = count

    num_with_max = len(instance_ids) - len(missing_summaries)
    print('Num instances', len(instance_ids))
    print('Num instances with all systems having summaries', num_with_max)
    print('Instnaces with missing summaries')
    print(json.dumps(missing_summaries, indent=2))


def save_data(data: List[Any], file_path: str) -> None:
    with JsonlWriter(file_path) as out:
        for item in data:
            out.write(item)


def setup(output_dir: str, force: bool) -> None:
    cnn_tar, dailymail_tar = download_tars(f'{output_dir}/raw', force)

    # Download the expert and turker annotations
    download_human_judgments(f'{output_dir}/raw', force)

    # Download the system outputs
    model_output_dir = download_system_outputs(f'{output_dir}/raw/model-outputs', force)

    # Untar all of the documents
    setup_documents(cnn_tar, dailymail_tar, output_dir, force)

    # Pair together the summaries and input documents. The script will output the
    # results into "model_annotations.aligned.paired.jsonl"
    run_pair_data(data_annotations=f'{output_dir}/raw/model_annotations.aligned.jsonl',
                  model_outputs=model_output_dir,
                  story_files=f'{output_dir}/raw')

    summaries, summaries_with_crowd, metrics = load_judgments(f'{output_dir}/raw/model_annotations.aligned.paired.jsonl')
    save_data(summaries, f'{output_dir}/summaries.jsonl')
    save_data(summaries_with_crowd, f'{output_dir}/summaries-with-crowd.jsonl')
    save_data(metrics, f'{output_dir}/metrics.jsonl')

    system_outputs = load_system_outputs(model_output_dir, summaries, f'{output_dir}/raw')
    save_data(system_outputs, f'{output_dir}/all-summaries.jsonl.gz')

    sanity_check(summaries, system_outputs, metrics)
    print_stats(system_outputs)
