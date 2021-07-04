DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

python -m sacrerouge bertscore score \
  --input-files datasets/fabbri2020/summaries.jsonl \
  --dataset-reader reference-based \
  --output-jsonl ${DIR}/output/fabbri2020/scores.jsonl

for metric in 'precision' 'recall' 'f1'; do
  python -m sacrerouge correlate \
    --metrics-jsonl-files datasets/fabbri2020/metrics.jsonl ${DIR}/output/fabbri2020/scores.jsonl \
    --metrics expert_relevance bertscore_${metric} \
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
      --input ${DIR}/output/fabbri2020/correlations/precision-${summarizer_type}.json BERTScore-P Fabbri2020 \
      --input ${DIR}/output/fabbri2020/correlations/recall-${summarizer_type}.json BERTScore-R Fabbri2020 \
      --input ${DIR}/output/fabbri2020/correlations/f1-${summarizer_type}.json BERTScore-F1 Fabbri2020
  done
done