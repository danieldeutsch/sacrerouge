DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

for method in blanc_help blanc_tune; do
  for dataset in cnn-dailymail dailynews dailynews-aspects; do
    for gap in 2 6; do
      python -m sacrerouge blanc score \
        --input-files datasets/vasilyev2020/${dataset}.summaries.jsonl \
        --dataset-reader document-based \
        --output-jsonl ${DIR}/output/vasilyev2020/${dataset}/${gap}/scores-${method}.jsonl \
        --show_progress_bar true \
        --blanc_type ${method} \
        --gap ${gap}
    done
  done
done

for method in blanc_help blanc_tune; do
  for dataset in cnn-dailymail dailynews; do
    for gap in 2 6; do
      python -m sacrerouge correlate \
          --metrics-jsonl-files datasets/vasilyev2020/${dataset}.metrics.jsonl ${DIR}/output/vasilyev2020/${dataset}/${gap}/scores-${method}.jsonl \
          --metrics generic_quality ${method} \
          --summarizer-type peer \
          --skip-summary-level \
          --skip-system-level \
          --output-file ${DIR}/output/vasilyev2020/${dataset}/${gap}/correlations/${method}-peer.json
    done
  done
done

for dataset in cnn-dailymail dailynews; do
  python -m sacrerouge.scripts.create_correlations_table \
    ${DIR}/output/tables/vasilyev2020/${dataset}.html \
    global \
    --input ${DIR}/output/vasilyev2020/${dataset}/2/correlations/blanc_help-peer.json BLANC-Help-Gap-2 ${dataset} \
    --input ${DIR}/output/vasilyev2020/${dataset}/6/correlations/blanc_help-peer.json BLANC-Help-Gap-6 ${dataset} \
    --input ${DIR}/output/vasilyev2020/${dataset}/2/correlations/blanc_help-peer.json BLANC-Tune-Gap-2 ${dataset} \
    --input ${DIR}/output/vasilyev2020/${dataset}/6/correlations/blanc_help-peer.json BLANC-Tune-Gap-6 ${dataset}
done