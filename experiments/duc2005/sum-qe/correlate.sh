DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

mkdir -p ${DIR}/output

for q in 'Q1' 'Q2' 'Q3' 'Q4' 'Q5'; do
  for split in 'all' 'reference' 'peer'; do
    python -m sacrerouge correlate \
      --metrics-jsonl-files datasets/duc-tac/duc2005/v1/task1.metrics.jsonl ${DIR}/output/scores.jsonl \
      --metrics linguistic_quality_${q} SumQE_${q} \
      --summarizer-type ${split} \
      --output-file ${DIR}/output/${split}/${q}.json
  done
done
