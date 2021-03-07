DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

for dataset in 'tac2008' 'tac2009' 'tac2010' 'tac2011'; do
  python -m sacrerouge supert score \
    ${DIR}/output/${dataset}/scores.jsonl \
    --dataset-reader split-document-based \
    --input-files datasets/duc-tac/${dataset}/v1.0/task1.A.jsonl datasets/duc-tac/${dataset}/v1.0/task1.A.summaries.jsonl \
    --environment_name /shared/ddeutsch/envs/supert \
    --log-file ${DIR}/output/${dataset}/log.log

  python -m sacrerouge correlate \
    --metrics-jsonl-files datasets/duc-tac/${dataset}/v1.0/task1.A.metrics.jsonl ${DIR}/output/${dataset}/scores.jsonl \
    --metrics overall_responsiveness supert \
    --summarizer-type peer \
    --output-file ${DIR}/output/${dataset}/correlations/peer.json \
    --log-file ${DIR}/output/${dataset}/correlations/log.log

  # No jackknifing necessary since it a referenceless metric
  python -m sacrerouge correlate \
    --metrics-jsonl-files datasets/duc-tac/${dataset}/v1.0/task1.A.metrics.jsonl ${DIR}/output/${dataset}/scores.jsonl \
    --metrics overall_responsiveness supert \
    --summarizer-type all \
    --output-file ${DIR}/output/${dataset}/correlations/all.json \
    --log-file ${DIR}/output/${dataset}/correlations/log.log
done

for summarizer_type in 'all' 'peer'; do
  for level in 'summary_level' 'system_level'; do
    python -m sacrerouge.scripts.create_correlations_table \
      ${DIR}/output/tables/${summarizer_type}-${level}.html \
      ${level} \
      --input ${DIR}/output/tac2008/correlations/${summarizer_type}.json SUPERT TAC2008 \
      --input ${DIR}/output/tac2009/correlations/${summarizer_type}.json SUPERT TAC2009 \
      --input ${DIR}/output/tac2010/correlations/${summarizer_type}.json SUPERT TAC2010 \
      --input ${DIR}/output/tac2011/correlations/${summarizer_type}.json SUPERT TAC2011
  done
done