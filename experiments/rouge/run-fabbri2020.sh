DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

python -m sacrerouge rouge score \
  --input-files datasets/fabbri2020/summaries.jsonl \
  --dataset-reader reference-based \
  --output-jsonl ${DIR}/output/fabbri2020/scores.jsonl \
  --log-file ${DIR}/output/fabbri2020/log.log \
  --compute_rouge_l true

for metric in 'rouge-1' 'rouge-2' 'rouge-l'; do
  for submetric in 'precision' 'recall' 'f1'; do
    python -m sacrerouge correlate \
      --metrics-jsonl-files datasets/fabbri2020/metrics.jsonl ${DIR}/output/fabbri2020/scores.jsonl \
      --metrics expert_relevance ${metric}_${submetric} \
      --summarizer-type peer \
      --output-file ${DIR}/output/fabbri2020/correlations/${metric}-${submetric}-peer.json \
      --log-file ${DIR}/output/fabbri2020/correlations/log.log
  done
done

for summarizer_type in 'peer'; do
  for level in 'summary_level' 'system_level'; do
    python -m sacrerouge.scripts.create_correlations_table \
      ${DIR}/output/tables/fabbri2020-${summarizer_type}-${level}.html \
      ${level} \
      --input ${DIR}/output/fabbri2020/correlations/rouge-1-precision-${summarizer_type}.json R1-P Fabbri2020 \
      --input ${DIR}/output/fabbri2020/correlations/rouge-1-recall-${summarizer_type}.json R1-R Fabbri2020 \
      --input ${DIR}/output/fabbri2020/correlations/rouge-1-f1-${summarizer_type}.json R1-F1 Fabbri2020 \
      --input ${DIR}/output/fabbri2020/correlations/rouge-2-precision-${summarizer_type}.json R2-P Fabbri2020 \
      --input ${DIR}/output/fabbri2020/correlations/rouge-2-recall-${summarizer_type}.json R2-R Fabbri2020 \
      --input ${DIR}/output/fabbri2020/correlations/rouge-2-f1-${summarizer_type}.json R2-F1 Fabbri2020 \
      --input ${DIR}/output/fabbri2020/correlations/rouge-l-precision-${summarizer_type}.json RL-P Fabbri2020 \
      --input ${DIR}/output/fabbri2020/correlations/rouge-l-recall-${summarizer_type}.json RL-R Fabbri2020 \
      --input ${DIR}/output/fabbri2020/correlations/rouge-l-f1-${summarizer_type}.json RL-F1 Fabbri2020
  done
done