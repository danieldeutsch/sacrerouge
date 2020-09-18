DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

for dataset in 'tac2008' 'tac2009' 'tac2010' 'tac2011'; do
  python -m sacrerouge qa-eval score \
    ${DIR}/output/${dataset}/scores.jsonl \
    --input-files datasets/duc-tac/${dataset}/v1.0/task1.A.summaries.jsonl \
    --dataset-reader reference-based \
    --log-file ${DIR}/output/${dataset}/log.log

  for metric in 'em' 'f1'; do
    python -m sacrerouge correlate \
      --metrics-jsonl-files datasets/duc-tac/${dataset}/v1.0/task1.A.metrics.jsonl ${DIR}/output/${dataset}/scores.jsonl \
      --metrics overall_responsiveness qa-eval_${metric} \
      --summarizer-type peer \
      --output-file ${DIR}/output/${dataset}/correlations/${metric}-peer.json \
      --log-file ${DIR}/output/${dataset}/correlations/log.log

    python -m sacrerouge correlate \
      --metrics-jsonl-files datasets/duc-tac/${dataset}/v1.0/task1.A.metrics.jsonl ${DIR}/output/${dataset}/scores.jsonl \
      --metrics overall_responsiveness qa-eval_jk_${metric} \
      --summarizer-type all \
      --output-file ${DIR}/output/${dataset}/correlations/${metric}-all.json \
      --log-file ${DIR}/output/${dataset}/correlations/log.log
  done
done

for summarizer_type in 'all' 'peer'; do
  for level in 'summary_level' 'system_level'; do
    python -m sacrerouge.scripts.create_correlations_table \
      ${DIR}/output/tables/${summarizer_type}-${level}.html \
      ${level} \
      --input ${DIR}/output/tac2008/correlations/em-${summarizer_type}.json QA-EM TAC2008 \
      --input ${DIR}/output/tac2009/correlations/em-${summarizer_type}.json QA-EM TAC2009 \
      --input ${DIR}/output/tac2010/correlations/em-${summarizer_type}.json QA-EM TAC2010 \
      --input ${DIR}/output/tac2011/correlations/em-${summarizer_type}.json QA-EM TAC2011 \
      --input ${DIR}/output/tac2008/correlations/f1-${summarizer_type}.json QA-F1 TAC2008 \
      --input ${DIR}/output/tac2009/correlations/f1-${summarizer_type}.json QA-F1 TAC2009 \
      --input ${DIR}/output/tac2010/correlations/f1-${summarizer_type}.json QA-F1 TAC2010 \
      --input ${DIR}/output/tac2011/correlations/f1-${summarizer_type}.json QA-F1 TAC2011
  done
done