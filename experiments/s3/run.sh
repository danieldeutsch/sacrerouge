DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

for dataset in 'tac2008' 'tac2009' 'tac2010' 'tac2011'; do
  python -m sacrerouge s3 score \
    ${DIR}/output/${dataset}/scores.jsonl \
    --input-files datasets/duc-tac/${dataset}/v1.0/task1.A.summaries.jsonl \
    --dataset-reader reference-based \
    --log-file ${DIR}/output/${dataset}/log.log \
    --environment_name /shared/ddeutsch/envs/s3

  for metric in 'pyr' 'resp'; do
    python -m sacrerouge correlate \
      --metrics-jsonl-files datasets/duc-tac/${dataset}/v1.0/task1.A.metrics.jsonl ${DIR}/output/${dataset}/scores.jsonl \
      --metrics overall_responsiveness s3_${metric} \
      --summarizer-type peer \
      --output-file ${DIR}/output/${dataset}/correlations/${metric}-peer.json \
      --log-file ${DIR}/output/${dataset}/correlations/log.log

    python -m sacrerouge correlate \
      --metrics-jsonl-files datasets/duc-tac/${dataset}/v1.0/task1.A.metrics.jsonl ${DIR}/output/${dataset}/scores.jsonl \
      --metrics overall_responsiveness s3_jk_${metric} \
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
      --input ${DIR}/output/tac2008/correlations/pyr-${summarizer_type}.json S3-Pyr TAC2008 \
      --input ${DIR}/output/tac2009/correlations/pyr-${summarizer_type}.json S3-Pyr TAC2009 \
      --input ${DIR}/output/tac2010/correlations/pyr-${summarizer_type}.json S3-Pyr TAC2010 \
      --input ${DIR}/output/tac2011/correlations/pyr-${summarizer_type}.json S3-Pyr TAC2011 \
      --input ${DIR}/output/tac2008/correlations/resp-${summarizer_type}.json S3-Resp TAC2008 \
      --input ${DIR}/output/tac2009/correlations/resp-${summarizer_type}.json S3-Resp TAC2009 \
      --input ${DIR}/output/tac2010/correlations/resp-${summarizer_type}.json S3-Resp TAC2010 \
      --input ${DIR}/output/tac2011/correlations/resp-${summarizer_type}.json S3-Resp TAC2011
  done
done