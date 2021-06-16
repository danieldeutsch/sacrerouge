import pickle
import re
from collections import defaultdict
from typing import Dict, List, Tuple

from sacrerouge.common.util import download_url_to_file, download_file_from_google_drive
from sacrerouge.data import Metrics, MetricsDict
from sacrerouge.io import JsonlWriter

FILE_IDS = {
    'banditsumm_out': {
        'src': '15q5345IommTx8IjEaXE8stbpHZoeVQWn',
        'ref': '1hqGynlbNeG07AFtZHDE47KZ-9ikvEO5_',
        'out': '17rkbNRMZYQuBFnExsiciBeWbHVJsP0Yy'
    },
    'bart_out': {
        'src': '1B4fo64Jc_rdrpTIuK_LqWdXpHv8T546l',
        'ref': '11DrHN4mI5w3eXdSh_scvrHVdO61d5E0O',
        'out': '1LiIVX-cqk4_Bf7Sw9gFw6SBZgyrF8foX'
    },
    'bottom_up_out': {
        'src': '1E14VYv3XzXp5d7ISefEFbR2v65RnW5TJ',
        'ref': '1mSVEh6ewwjYFYsQc1uTx8CLqzbmBMEX4',
        'out': '1QwgY0EXAkUf7xi08FekRtGLL5FFITgfx'
    },
    'fast_abs_rl_out_rerank': {
        'src': '1mXR4I62uso5SMCBdXSeAAUxF5EN96rwu',
        'ref': '1Piy8hg9Xrh5WVSifmJAz7R11TwvNipQC',
        'out': '1XJyBnQaK7F6ZWLr1f9dmEA8ahBsb-n71'
    },
    'heter_graph_out': {
        'src': '1hLPtWV1puUF4MAEP5k6shbqUJdVl_yTN',
        'ref': '1DQbpzuqSl9JAPj1hJK7ZRrfRbysK_B6r',
        'out': '1mFxDFXAC2cdkKSmeBccOTtcq1Nv0zZRO'
    },
    'matchsumm_out': {
        'src': '1V1NDfucZTOBWSoFRiwXn7nOobbIITWbn',
        'ref': '1tZSetqois0BuS1WUBDRI4qqi2I92RTwu',
        'out': '18q_CbdE5S5pq_GkbLUxvjFwZYyS0yoPX'
    },
    'neusumm_out': {
        'src': '1h_h6lJz6h0mwzfbisgFLBNEdolKz95Py',
        'ref': '1JM9DXmBM2N3yPqO_dNii3Q9NMX5W9p1J',
        'out': '179rmNlBY4Q_cK6b_amqoKk0Dx2PAMjBB',
    },
    'pnbert_out_bert_lstm_pn': {
        'src': '1wMxjAcb9Q3pkiFlk2YgzmG66kXkXLWjy',
        'ref': '1FPtb3gosX0mz__vsYJ454SdUR6oBPK_R',
        'out': '10ppCHPGxv3CPs-Cp7sINq6YdmFp9m3Ci'
    },
    'pnbert_out_bert_lstm_pn_rl': {
        'src': '1OktnpQWcOvQUam7SHCHFm2OHTa-YwFNJ',
        'ref': '1OB7W9WaIiBxj_uKdNuOVRBdic923TnU6',
        'out': '18tC3jVN_ktyTq2_YZ8OQTNZ73XJgpmhv'
    },
    'pnbert_out_bert_tf_pn': {
        'src': '1XeYU68II8bw7FN6XyAbDMaTuD8dCx7Fh',
        'ref': '1Tiv-w0dVP1H3PM6XF-88hM9GSZF1xwBr',
        'out': '1nr11C6C47ixn0nEUS49tzHjVMj9hQSft'
    },
    'pnbert_out_bert_tf_sl': {
        'src': '1p6IKQDhtfxbm-2g6pgKsqpShTS2QhQq7',
        'ref': '1hgQZnNReTruX4Ag2v7xM6lZbQTSi5_wn',
        'out': '1i2GtoOhHhbQGxKf38j0FcNuI-B8F866L'
    },
    'pnbert_out_lstm_pn_rl': {
        'src': '1Zb-DRjnyrH21GsIUQjXU3vRedfMC330_',
        'ref': '1l-7CrF5cXUR4vd6XQhAiEC7vNxHlX3GC',
        'out': '1arRQxV7Emn1ia-2J-IhKEdh8BkUwLLSG'
    },
    'presumm_out_abs': {
        'src': '1IyS2c5ZhpmShAhiiVBV6WxKfpyKPtvcg',
        'ref': '1_BrRh_DklSM8RUFo9qCi1rNOryrKwLdN',
        'out': '120kvLHHnAYGy-QJo3GPWS34kYYMbl99K'
    },
    'presumm_out_ext_abs': {
        'src': '1Eh4n2N3dgJtIBZD4oxj2vptVOy1jC2j0',
        'ref': '1bYIWltkFAYn3d_EcVsRxBClqq1NK5Hck',
        'out': '1Eh4n2N3dgJtIBZD4oxj2vptVOy1jC2j0'
    },
    'presumm_out_trans_abs': {
        'src': '1TwDkwf_M-fck4kQF9VdefG-qPCMrj2yR',
        'ref': '1lmYGJRWdD4aKcQo3GyUttbja_WnnFPoL',
        'out': '13zVlhxyjcsnwnzsdwSGcbgeySusZVQW7'
    },
    'ptr_generator_out_pointer_gen_cov': {
        'src': '13TNp37VKabS8N_2k86PNrymjz7mEp_5C',
        'ref': '1m4O_DH-OsUbJXXWOuheuiVx2LKvgMPZr',
        'out': '1aK6hD21frEzuyW99244aFOlh81VoPNqI'
    },
    'refresh_out': {
        'src': '1FAKShjtVnSIXnXlpgkAjX6TKIkr6bEp4',
        'ref': '1EdZ_Al50jQC-K2R1swuZWK4tlhH_-oTv',
        'out': '1Y5iALSwSs_5NUg-5YIgp1Jb5iSIcMUqv'
    },
    'semsim_out': {
        'src': '1Yy6nV6kLgy4iB62HqTj--QNcu4Oyj9Zc',
        'ref': '19yAw09pLDAeG8vwX8a1mFPtNW1Er6TLR',
        'out': '10E-AYRN79LtSpqBoH1fqit-c2_hVrvPV'
    },
    't5_out_11B': {
        'src': '1H5-Nvelsz3a6h6VzqrOUtU2bAzv9abcD',
        'ref': '1FKBrL-DzR0SaaLTYyDaHwkSq3HGVuNYA',
        'out': '15kmkjQSi0BlvI6W39bugN9IVM5d77ytX'
    },
    't5_out_base': {
        'src': '1VaGXeU5U73uiUdEh8wyb8XDsWQbgjIq6',
        'ref': '1dc-qblHY19smGa8BKK8ZIB8VhFbQBgoW',
        'out': '1upsVycGT91Z94Jdkj34N1A2hw1uvy-Vl'
    },
    't5_out_large': {
        'src': '1sePwJBrQyazWzgAHWRGSIy0R1I0RopJ3',
        'ref': '1jgGFfXa3uAKvH66ujCyto9k45f9s2S4P',
        'out': '1Qiny9zc7COwBq1LtYBtQno5WhhVFcm4q'
    },
    'two_stage_rl_out': {
        'src': '1GV4-9iw9UK09fJAGMZDk9au4Pniic--s',
        'ref': '1lyl9Hn92T9gtF-qtlJtb_obW7uc0cWGu',
        'out': '1voH6p17Z-Rd-_m8Reu86D6TjuwqSG2_H'
    },
    'unilm_out_v1': {
        'src': '1q2WPIUpTQFb8WZEc2hAZNcirIRwDboMx',
        'ref': '1xpjJqNmn_6BFneb5QB9tgpfuAA0cWlak',
        'out': '1AmOhAsmA-kV-PSJSAedg7hSCTJ9_2FVP'
    },
    'unilm_out_v2': {
        'src': '1CgLfz_TNLyAniRNfFKeEZFtDbYFivo_V',
        'ref': '1nuUWeSBWw27hYZlKv9N-ljdB1o5dBmVL',
        'out': '1HyeWRCPjOazOxE3LXx_BmoH6CI2YZkI0'
    },
}

ABSTRACTIVE = {
    'bottom_up_out', 'fast_abs_rl_out_rerank', 'presumm_out_abs', 'presumm_out_ext_abs',
    'presumm_out_trans_abs', 'ptr_generator_out_pointer_gen_cov', 'semsim_out', 't5_out_11B', 't5_out_base',
    't5_out_large', 'two_stage_rl_out', 'unilm_out_v1', 'unilm_out_v2'
}
EXTRACTIVE = {
    'banditsumm_out', 'bart_out', 'heter_graph_out', 'matchsumm_out', 'neusumm_out', 'pnbert_out_bert_lstm_pn',
    'pnbert_out_bert_lstm_pn_rl', 'pnbert_out_bert_tf_pn', 'pnbert_out_bert_tf_sl', 'pnbert_out_lstm_pn_rl', 'refresh_out',
}


def download_raw_data(output_dir: str, force: bool) -> None:
    for summarizer_id, file_ids in FILE_IDS.items():
        for filename, file_id in file_ids.items():
            if file_id is not None:
                download_file_from_google_drive(file_id, f'{output_dir}/raw/{summarizer_id}/{filename}.txt', force=force)


def load_all_data(output_dir: str) -> Tuple[Dict, Dict]:
    abs_data = {}
    ext_data = {}
    for summarizer_id in FILE_IDS.keys():
        if summarizer_id in ABSTRACTIVE:
            data = abs_data
        elif summarizer_id in EXTRACTIVE:
            data = ext_data
        else:
            raise Exception(f'Could not find {summarizer_id}')

        data[summarizer_id] = {
            'src': list(map(lambda line: line.strip(), open(f'{output_dir}/raw/{summarizer_id}/src.txt', 'r').read().splitlines())),
            'ref': list(map(lambda line: line.strip(), open(f'{output_dir}/raw/{summarizer_id}/ref.txt', 'r').read().splitlines())),
            'out': list(map(lambda line: line.strip(), open(f'{output_dir}/raw/{summarizer_id}/out.txt', 'r').read().splitlines()))
        }
        assert len(data[summarizer_id]['src']) == len(data[summarizer_id]['ref']) == len(data[summarizer_id]['out'])
    return abs_data, ext_data


def get_annotated_summaries(data: Dict):
    summaries = defaultdict(dict)
    for instance_dict in data.values():
        doc_id = str(instance_dict['doc_id'])
        for summarizer_id, summarizer_dict in instance_dict['system_summaries'].items():
            summaries[summarizer_id][summarizer_dict['system_summary'].strip()] = doc_id
    return summaries


def filter_to_scored_summaries(raw_data: Dict, annotated_data: Dict):
    annotated_summaries = get_annotated_summaries(annotated_data)
    filtered = {}
    for summarizer_id in raw_data.keys():
        indices_to_keep = []
        doc_ids = []
        for i, output in enumerate(raw_data[summarizer_id]['out']):
            if output in annotated_summaries[summarizer_id + '.txt']:
                doc_id = annotated_summaries[summarizer_id + '.txt'][output]
                indices_to_keep.append(i)
                doc_ids.append(doc_id)
        if len(indices_to_keep) != 100:
            raise Exception(f'Could not successfully match the 100 outputs for system {summarizer_id}. This is most '
                            f'likely because Google Drive began denying the download request for all of the system outputs. '
                            f'Please delete the directory: <output-dir>/raw/{summarizer_id} and try again.')

        filtered[summarizer_id] = {doc_id: {
            'src': raw_data[summarizer_id]['src'][i],
            'ref': raw_data[summarizer_id]['ref'][i],
            'out': raw_data[summarizer_id]['out'][i]
        } for i, doc_id in zip(indices_to_keep, doc_ids)}
    return filtered


def split_into_sentences(text: str) -> List[str]:
    assert text.startswith('<t>')
    sentence_regex = '<t> (.+?) </t>'
    sentences = []
    for match in re.findall(sentence_regex, text):
        sentences.append(match)
    assert len(sentences) > 0
    return sentences


def convert_to_sacrerouge_instances_and_metrics(annotated_data: Dict, filtered_data: Dict, split: str) -> Tuple[List[Dict], List[Metrics]]:
    instances = []
    metrics_list = []
    for instance_dict in annotated_data.values():
        instance_id = str(instance_dict['doc_id'])

        for summarizer_id, summarizer_dict in instance_dict['system_summaries'].items():
            summarizer_id = summarizer_id[:-4]  # strip .txt
            if split == 'abs' and summarizer_id == 'bart_out':
                # This should not be included in the abstractive models. See the Readme about
                # this dataset
                continue

            document_text = filtered_data[summarizer_id][instance_id]['src']
            if '<t>' in document_text:
                document_text = split_into_sentences(document_text)
            document = {'text': document_text}

            summary = {'text': split_into_sentences(filtered_data[summarizer_id][instance_id]['out'])}
            reference = {
                'summarizer_id': 'ground-truth',
                'summarizer_type': 'reference',
                'text': split_into_sentences(filtered_data[summarizer_id][instance_id]['ref'])
            }

            metrics_dict = MetricsDict({
                'rouge-1': {
                    'precision': float(summarizer_dict['scores']['rouge_1_precision']),
                    'recall': float(summarizer_dict['scores']['rouge_1_recall']),
                    'f1': float(summarizer_dict['scores']['rouge_1_f_score'])
                },
                'rouge-2': {
                    'precision': float(summarizer_dict['scores']['rouge_2_precision']),
                    'recall': float(summarizer_dict['scores']['rouge_2_recall']),
                    'f1': float(summarizer_dict['scores']['rouge_2_f_score'])
                },
                'rouge-l': {
                    'precision': float(summarizer_dict['scores']['rouge_l_precision']),
                    'recall': float(summarizer_dict['scores']['rouge_l_recall']),
                    'f1': float(summarizer_dict['scores']['rouge_l_f_score'])
                },
                'js-2': float(summarizer_dict['scores']['js-2']),
                'MoverScore': float(summarizer_dict['scores']['mover_score']),
                'bertscore': {
                    'precision': float(summarizer_dict['scores']['bert_precision_score']),
                    'recall': float(summarizer_dict['scores']['bert_recall_score']),
                    'f1': float(summarizer_dict['scores']['bert_precision_score']),
                },
                'litepyramid': {
                    'recall': float(summarizer_dict['scores']['litepyramid_recall'])
                }
            })
            instances.append({
                'instance_id': instance_id,
                'summarizer_id': summarizer_id,
                'summarizer_type': 'peer',
                'references': [reference],
                'summary': summary,
                'documents': [document]
            })
            metrics_list.append(Metrics(instance_id, summarizer_id, 'peer', metrics_dict))
    return instances, metrics_list


def save_to_jsonl(data: List, output_file: str) -> None:
    with JsonlWriter(output_file) as out:
        for item in data:
            out.write(item)


def setup(output_dir: str, force: bool = False) -> None:
    download_raw_data(output_dir, force)
    abs_raw_data, ext_raw_data = load_all_data(output_dir)

    download_url_to_file('https://github.com/neulab/REALSumm/raw/master/scores_dicts/abs.pkl', f'{output_dir}/raw/abs.pkl', force=force)
    download_url_to_file('https://github.com/neulab/REALSumm/raw/master/scores_dicts/ext.pkl', f'{output_dir}/raw/ext.pkl', force=force)

    abstractive = pickle.load(open(f'{output_dir}/raw/abs.pkl', 'rb'))
    extractive = pickle.load(open(f'{output_dir}/raw/ext.pkl', 'rb'))

    abs_filtered = filter_to_scored_summaries(abs_raw_data, abstractive)
    ext_filtered = filter_to_scored_summaries(ext_raw_data, extractive)

    abs_instances, abs_metrics_list = convert_to_sacrerouge_instances_and_metrics(abstractive, abs_filtered, 'abs')
    ext_instances, ext_metrics_list = convert_to_sacrerouge_instances_and_metrics(extractive, ext_filtered, 'ext')

    save_to_jsonl(abs_instances, f'{output_dir}/summaries-abs.jsonl')
    save_to_jsonl(ext_instances, f'{output_dir}/summaries-ext.jsonl')
    save_to_jsonl(abs_instances + ext_instances, f'{output_dir}/summaries-mix.jsonl')

    save_to_jsonl(abs_metrics_list, f'{output_dir}/metrics-abs.jsonl')
    save_to_jsonl(ext_metrics_list, f'{output_dir}/metrics-ext.jsonl')
    save_to_jsonl(abs_metrics_list + ext_metrics_list, f'{output_dir}/metrics-mix.jsonl')