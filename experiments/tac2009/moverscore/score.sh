DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

mkdir -p ${DIR}/output

python -m sacrerouge score \
  ${DIR}/config.json \
  ${DIR}/output/scores.A.jsonl \
  --overrides '{"dataset_reader.input_jsonl": "datasets/duc-tac/tac2008/v1.0/task1.A.summaries.jsonl"}'

python -m sacrerouge score \
  ${DIR}/config.json \
  ${DIR}/output/scores.B.jsonl \
  --overrides '{"dataset_reader.input_jsonl": "datasets/duc-tac/tac2008/v1.0/task1.B.summaries.jsonl"}'

python -m sacrerouge score \
  ${DIR}/config.json \
  ${DIR}/output/scores.A-B.jsonl \
  --overrides '{"dataset_reader.input_jsonl": "datasets/duc-tac/tac2008/v1.0/task1.A-B.summaries.jsonl"}'
