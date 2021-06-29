DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

for method in blanc_help blanc_tune; do
  python -m sacrerouge blanc score \
    --input-files datasets/fabbri2020/summaries.jsonl \
    --dataset-reader document-based \
    --output-jsonl ${DIR}/output/fabbri2020/scores-${method}.jsonl \
    --log-file ${DIR}/output/fabbri2020/log.log \
    --blanc_type ${method}

  for metric in relevance consistency fluency coherence; do
    python -m sacrerouge correlate \
      --metrics-jsonl-files datasets/fabbri2020/metrics.jsonl ${DIR}/output/fabbri2020/scores-${method}.jsonl \
      --metrics expert_${metric} ${method} \
      --summarizer-type peer \
      --output-file ${DIR}/output/fabbri2020/correlations/${metric}/${method}.json \
      &
    done
    wait
done

for metric in relevance consistency fluency coherence; do
  for level in 'global' 'summary_level' 'system_level'; do
    python -m sacrerouge.scripts.create_correlations_table \
      ${DIR}/output/tables/fabbri2020-${level}.html \
      ${level} \
      --input ${DIR}/output/fabbri2020/correlations/${metric}/blanc_help.json BLANC-Help Fabbri2020 \
      --input ${DIR}/output/fabbri2020/correlations/${metric}/blanc_tune.json BLANC-Tune Fabbri2020
  done
done