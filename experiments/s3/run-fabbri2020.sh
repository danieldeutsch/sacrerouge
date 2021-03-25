DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

python -m sacrerouge s3 score \
  --input-files datasets/fabbri2020/summaries.jsonl \
  --dataset-reader reference-based \
  --output-jsonl ${DIR}/output/fabbri2020/scores.jsonl \
  --log-file ${DIR}/output/fabbri2020/log.log \
  --environment_name /shared/ddeutsch/envs/s3

for metric in 'pyr' 'resp'; do
  python -m sacrerouge correlate \
    --metrics-jsonl-files datasets/fabbri2020/metrics.jsonl ${DIR}/output/fabbri2020/scores.jsonl \
    --metrics expert_relevance s3_${metric} \
    --summarizer-type peer \
    --output-file ${DIR}/output/fabbri2020/correlations/${metric}-peer.json \
    --log-file ${DIR}/output/fabbri2020/correlations/log.log
done

for summarizer_type in 'peer'; do
  for level in 'summary_level' 'system_level'; do
    python -m sacrerouge.scripts.create_correlations_table \
      ${DIR}/output/tables/fabbri2020-${summarizer_type}-${level}.html \
      ${level} \
      --input ${DIR}/output/fabbri2020/correlations/pyr-${summarizer_type}.json S3-Pyr Fabbri2020 \
      --input ${DIR}/output/fabbri2020/correlations/resp-${summarizer_type}.json S3-Resp Fabbri2020
  done
done