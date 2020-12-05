DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

for dataset in cnndm xsum; do
  python -m sacrerouge feqa score \
    --input-files datasets/wang2020/${dataset}.summaries.jsonl \
    --dataset-reader document-based \
    --output-jsonl ${DIR}/output/${dataset}/scores.jsonl \
    --environment_name /shared/ddeutsch/envs/feqa

  python -m sacrerouge correlate \
    --metrics-jsonl-files datasets/wang2020/${dataset}.metrics.jsonl ${DIR}/output/${dataset}/scores.jsonl \
    --metrics wang2020_crowd_faithfulness FEQA \
    --summarizer-type peer \
    --skip-summary-level \
    --skip-system-level \
    --output-file ${DIR}/output/${dataset}/correlations.json
done