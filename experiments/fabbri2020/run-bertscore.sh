DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

python -m sacrerouge bertscore score \
  ${DIR}/output/single-reference/scores/bertscore.jsonl \
  --input-files datasets/fabbri2020/summaries.jsonl \
  --dataset-reader reference-based \
  --log-file ${DIR}/output/log.log

python -m sacrerouge bertscore score \
  ${DIR}/output/multi-reference/scores/bertscore.jsonl \
  --input-files datasets/fabbri2020/summaries-with-crowd.jsonl \
  --dataset-reader reference-based \
  --log-file ${DIR}/output/log.log

for reference in 'single-reference' 'multi-reference'; do
  for metric in 'precision' 'recall' 'f1'; do
    python -m sacrerouge correlate \
      --metrics-jsonl-files datasets/fabbri2020/metrics.jsonl ${DIR}/output/${reference}/scores/bertscore.jsonl \
      --metrics expert_relevance bertscore_${metric} \
      --summarizer-type peer \
      --output-file ${DIR}/output/${reference}/correlations/bertscore/${metric}.json \
      --log-file ${DIR}/output/${reference}/correlations/log.log
  done
done