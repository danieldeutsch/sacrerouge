DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

python -m sacrerouge score ${DIR}/config.json ${DIR}/output/scores.jsonl
