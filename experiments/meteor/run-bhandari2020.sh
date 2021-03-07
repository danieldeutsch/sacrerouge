DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

for split in 'abs' 'ext' 'mix'; do
    python -m sacrerouge meteor score \
      --input-files datasets/bhandari2020/summaries-${split}.jsonl \
      --dataset-reader reference-based \
      --output-jsonl ${DIR}/output/bhandari2020/scores-${split}.jsonl \
      --log-file ${DIR}/output/bhandari2020/log.log

    python -m sacrerouge correlate \
      --metrics-jsonl-files datasets/bhandari2020/metrics-${split}.jsonl ${DIR}/output/bhandari2020/scores-${split}.jsonl \
      --metrics litepyramid_recall METEOR \
      --summarizer-type peer \
      --output-file ${DIR}/output/bhandari2020/correlations/${split}/METEOR-peer.json \
      --log-file ${DIR}/output/bhandari2020/correlations/log.log
done

for summarizer_type in 'peer'; do
  for level in 'summary_level' 'system_level'; do
    python -m sacrerouge.scripts.create_correlations_table \
      ${DIR}/output/tables/bhandari2020/${summarizer_type}-${level}.html \
      ${level} \
      --input ${DIR}/output/bhandari2020/correlations/abs/METEOR-${summarizer_type}.json METEOR Bhandari2020-Abs \
      --input ${DIR}/output/bhandari2020/correlations/ext/METEOR-${summarizer_type}.json METEOR Bhandari2020-Ext \
      --input ${DIR}/output/bhandari2020/correlations/mix/METEOR-${summarizer_type}.json METEOR Bhandari2020-Mix
  done
done