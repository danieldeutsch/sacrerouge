DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

python -m sacrerouge moverscore score \
  ${DIR}/output/single-reference/scores/moverscore.jsonl \
  --input-files datasets/fabbri2020/summaries.jsonl \
  --dataset-reader reference-based \
  --log-file ${DIR}/output/log.log

python -m sacrerouge moverscore score \
  ${DIR}/output/multi-reference/scores/moverscore.jsonl \
  --input-files datasets/fabbri2020/summaries-with-crowd.jsonl \
  --dataset-reader reference-based \
  --log-file ${DIR}/output/log.log

for reference in 'single-reference' 'multi-reference'; do
  python -m sacrerouge correlate \
    --metrics-jsonl-files datasets/fabbri2020/metrics.jsonl ${DIR}/output/${reference}/scores/moverscore.jsonl \
    --metrics expert_relevance MoverScore \
    --summarizer-type peer \
    --output-file ${DIR}/output/${reference}/correlations/moverscore.json \
    --log-file ${DIR}/output/${reference}/correlations/log.log
done