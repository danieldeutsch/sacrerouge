DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

python -m sacrerouge bewte score \
  --input-files datasets/fabbri2020/summaries.jsonl \
  --dataset-reader reference-based \
  --output-jsonl ${DIR}/output/fabbri2020/scores.jsonl \
  --log-file ${DIR}/output/fabbri2020/log.log

for metric in 'precision' 'recall' 'f1'; do
  python -m sacrerouge correlate \
    --metrics-jsonl-files datasets/fabbri2020/metrics.jsonl ${DIR}/output/fabbri2020/scores.jsonl \
    --metrics expert_relevance BEwTE_${metric} \
    --summarizer-type peer \
    --output-file ${DIR}/output/fabbri2020/correlations/${metric}-peer.json \
    --log-file ${DIR}/output/fabbri2020/correlations/log.log \
    &
done
wait

for summarizer_type in 'peer'; do
  for level in 'summary_level' 'system_level'; do
    python -m sacrerouge.scripts.create_correlations_table \
      ${DIR}/output/tables/fabbri2020-${summarizer_type}-${level}.html \
      ${level} \
      --input ${DIR}/output/fabbri2020/correlations/precision-${summarizer_type}.json BEwTE-P Fabbri2020 \
      --input ${DIR}/output/fabbri2020/correlations/recall-${summarizer_type}.json BEwTE-R Fabbri2020 \
      --input ${DIR}/output/fabbri2020/correlations/f1-${summarizer_type}.json BEwTE-F1 Fabbri2020
  done
done