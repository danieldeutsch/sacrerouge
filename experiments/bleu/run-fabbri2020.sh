DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

python -m sacrerouge sent-bleu score \
  --input-files datasets/fabbri2020/summaries.jsonl \
  --dataset-reader reference-based \
  --output-jsonl ${DIR}/output/fabbri2020/scores.jsonl \
  --log-file ${DIR}/output/fabbri2020/log.log

python -m sacrerouge correlate \
  --metrics-jsonl-files datasets/fabbri2020/metrics.jsonl ${DIR}/output/fabbri2020/scores.jsonl \
  --metrics expert_relevance sent-bleu \
  --summarizer-type peer \
  --output-file ${DIR}/output/fabbri2020/correlations.json \
  --log-file ${DIR}/output/fabbri2020/log.log

for level in 'summary_level' 'system_level'; do
  python -m sacrerouge.scripts.create_correlations_table \
    ${DIR}/output/tables/fabbri2020-${level}.html \
    ${level} \
    --input ${DIR}/output/fabbri2020/correlations.json SentBLEU Fabbri2020
done
