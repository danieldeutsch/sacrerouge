DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

for split in 'abs' 'ext' 'mix'; do
    python -m sacrerouge supert score \
      --input-files datasets/bhandari2020/summaries-${split}.jsonl  \
      --dataset-reader document-based \
      --output-jsonl ${DIR}/output/bhandari2020/scores-${split}.jsonl \
      --environment_name /shared/ddeutsch/envs/supert \
      --log-file ${DIR}/output/bhandari2020/log.log

    python -m sacrerouge correlate \
      --metrics-jsonl-files datasets/bhandari2020/metrics-${split}.jsonl ${DIR}/output/bhandari2020/scores-${split}.jsonl \
      --metrics litepyramid_recall supert \
      --summarizer-type peer \
      --output-file ${DIR}/output/bhandari2020/correlations/${split}/peer.json \
      --log-file ${DIR}/output/bhandari2020/correlations/log.log
done

for summarizer_type in 'peer'; do
  for level in 'summary_level' 'system_level'; do
    python -m sacrerouge.scripts.create_correlations_table \
      ${DIR}/output/tables/bhandari2020/${summarizer_type}-${level}.html \
      ${level} \
      --input ${DIR}/output/bhandari2020/correlations/abs/${summarizer_type}.json SUPERT Bhandari2020-Abs \
      --input ${DIR}/output/bhandari2020/correlations/ext/${summarizer_type}.json SUPERT Bhandari2020-Ext \
      --input ${DIR}/output/bhandari2020/correlations/mix/${summarizer_type}.json SUPERT Bhandari2020-Mix
  done
done