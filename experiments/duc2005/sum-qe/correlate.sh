DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

mkdir -p ${DIR}/output

for split in 'A-B'; do
  python -m sacrerouge correlate \
    --metrics-jsonl-files datasets/duc-tac/tac2008/v1.0/task1.${split}.metrics.jsonl ${DIR}/output/scores.${split}.jsonl \
    --metrics overall_responsiveness AutoSummENG \
    --summarizer-type peer \
    --output-file ${DIR}/output/${split}/peers/responsiveness_autosummeng.json \
    --silent

  # python -m sacrerouge correlate \
  #   --metrics-jsonl-files datasets/duc-tac/tac2008/v1.0/task1.${split}.metrics.jsonl ${DIR}/output/scores.${split}.jsonl \
  #   --metrics overall_responsiveness AutoSummENG_jk \
  #   --summarizer-type reference \
  #   --output-file ${DIR}/output/${split}/references/responsiveness_autosummeng.json \
  #   --silent
  #
  # python -m sacrerouge correlate \
  #   --metrics-jsonl-files datasets/duc-tac/tac2008/v1.0/task1.${split}.metrics.jsonl ${DIR}/output/scores.${split}.jsonl \
  #   --metrics overall_responsiveness AutoSummENG_jk \
  #   --summarizer-type all \
  #   --output-file ${DIR}/output/${split}/all/responsiveness_autosummeng.json \
  #   --silent
done
