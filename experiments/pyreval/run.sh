DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

for dataset in tac2008 tac2009 tac2010 tac2011; do
  python -m sacrerouge pyreval score \
    ${DIR}/output/${dataset}/scores.jsonl \
    --input-files datasets/duc-tac/${dataset}/v1.0/task1.A.summaries.jsonl \
    --dataset-reader reference-based \
    --verbose true \
    --environment_name /shared/ddeutsch/envs/pyreval \
    --log-file ${DIR}/output/${dataset}/log.log

  for metric in raw quality coverage comprehensive; do
    python -m sacrerouge correlate \
      --metrics-jsonl-files datasets/duc-tac/${dataset}/v1.0/task1.A.metrics.jsonl ${DIR}/output/${dataset}/scores.jsonl \
      --metrics overall_responsiveness pyreval_${metric} \
      --summarizer-type peer \
      --output-file ${DIR}/output/${dataset}/correlations/${metric}-peer.json \
      --log-file ${DIR}/output/${dataset}/correlations/log.log

    python -m sacrerouge correlate \
      --metrics-jsonl-files datasets/duc-tac/${dataset}/v1.0/task1.A.metrics.jsonl ${DIR}/output/${dataset}/scores.jsonl \
      --metrics overall_responsiveness pyreval_jk_${metric} \
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
      --input ${DIR}/output/tac2008/correlations/raw-${summarizer_type}.json Raw TAC2008 \
      --input ${DIR}/output/tac2009/correlations/raw-${summarizer_type}.json Raw TAC2009 \
      --input ${DIR}/output/tac2010/correlations/raw-${summarizer_type}.json Raw TAC2010 \
      --input ${DIR}/output/tac2011/correlations/raw-${summarizer_type}.json Raw TAC2011 \
      --input ${DIR}/output/tac2008/correlations/quality-${summarizer_type}.json Quality TAC2008 \
      --input ${DIR}/output/tac2009/correlations/quality-${summarizer_type}.json Quality TAC2009 \
      --input ${DIR}/output/tac2010/correlations/quality-${summarizer_type}.json Quality TAC2010 \
      --input ${DIR}/output/tac2011/correlations/quality-${summarizer_type}.json Quality TAC2011 \
      --input ${DIR}/output/tac2008/correlations/coverage-${summarizer_type}.json Coverage TAC2008 \
      --input ${DIR}/output/tac2009/correlations/coverage-${summarizer_type}.json Coverage TAC2009 \
      --input ${DIR}/output/tac2010/correlations/coverage-${summarizer_type}.json Coverage TAC2010 \
      --input ${DIR}/output/tac2011/correlations/coverage-${summarizer_type}.json Coverage TAC2011 \
      --input ${DIR}/output/tac2008/correlations/comprehensive-${summarizer_type}.json Comprehensive TAC2008 \
      --input ${DIR}/output/tac2009/correlations/comprehensive-${summarizer_type}.json Comprehensive TAC2009 \
      --input ${DIR}/output/tac2010/correlations/comprehensive-${summarizer_type}.json Comprehensive TAC2010 \
      --input ${DIR}/output/tac2011/correlations/comprehensive-${summarizer_type}.json Comprehensive TAC2011
  done
done