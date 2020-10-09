DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

python -m sacrerouge rouge score \
  ${DIR}/output/single-reference/scores/rouge.jsonl \
  --input-files datasets/fabbri2020/summaries.jsonl \
  --dataset-reader reference-based \
  --log-file ${DIR}/output/log.log

python -m sacrerouge rouge score \
  ${DIR}/output/multi-reference/scores/rouge.jsonl \
  --input-files datasets/fabbri2020/summaries-with-crowd.jsonl \
  --dataset-reader reference-based \
  --log-file ${DIR}/output/log.log

for reference in 'single-reference' 'multi-reference'; do
  for metric in 'rouge-1' 'rouge-2'; do
    for submetric in 'precision' 'recall' 'f1'; do
      python -m sacrerouge correlate \
        --metrics-jsonl-files datasets/fabbri2020/metrics.jsonl ${DIR}/output/${reference}/scores/rouge.jsonl \
        --metrics expert_relevance ${metric}_${submetric} \
        --summarizer-type peer \
        --output-file ${DIR}/output/${reference}/correlations/${metric}/${submetric}.json \
        --log-file ${DIR}/output/${reference}/correlations/log.log
    done
  done
done