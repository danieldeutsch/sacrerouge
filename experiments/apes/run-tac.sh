DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

for dataset in 'tac2008' 'tac2009' 'tac2010' 'tac2011'; do
  python -m sacrerouge apes score \
    --output-jsonl ${DIR}/output/${dataset}/scores.jsonl \
    --input-files datasets/duc-tac/${dataset}/v1.0/task1.A.summaries.jsonl \
    --dataset-reader reference-based \
    --verbose true \
    --environment_name /shared/ddeutsch/envs/apes > stdout-${dataset}.txt

  python -m sacrerouge correlate \
    --metrics-jsonl-files datasets/duc-tac/${dataset}/v1.0/task1.A.metrics.jsonl ${DIR}/output/${dataset}/scores.jsonl \
    --metrics overall_responsiveness APES \
    --summarizer-type peer \
    --output-file ${DIR}/output/${dataset}/correlations/peer.json \
    --log-file ${DIR}/output/${dataset}/correlations/log.log

  python -m sacrerouge correlate \
    --metrics-jsonl-files datasets/duc-tac/${dataset}/v1.0/task1.A.metrics.jsonl ${DIR}/output/${dataset}/scores.jsonl \
    --metrics overall_responsiveness APES_jk \
    --summarizer-type all \
    --output-file ${DIR}/output/${dataset}/correlations/all.json \
    --log-file ${DIR}/output/${dataset}/correlations/log.log
done

for summarizer_type in 'all' 'peer'; do
  for level in 'summary_level' 'system_level'; do
    python -m sacrerouge.scripts.create_correlations_table \
      ${DIR}/output/tables/${summarizer_type}-${level}.html \
      ${level} \
      --input ${DIR}/output/tac2008/correlations/${summarizer_type}.json APES TAC2008 \
      --input ${DIR}/output/tac2009/correlations/${summarizer_type}.json APES TAC2009
  done
done