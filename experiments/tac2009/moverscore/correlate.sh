DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

mkdir -p ${DIR}/output

for split in 'A' 'B' 'A-B'; do
  python -m sacrerouge correlate \
    --metrics-jsonl-files datasets/duc-tac/tac2008/v1.0/task1.${split}.metrics.jsonl ${DIR}/output/scores.${split}.jsonl \
    --metrics overall_responsiveness MoverScore \
    --summarizer-type peer \
    --output-file ${DIR}/output/${split}/peers/responsiveness_moverscore.json \
    --silent

  python -m sacrerouge correlate \
    --metrics-jsonl-files datasets/duc-tac/tac2008/v1.0/task1.${split}.metrics.jsonl ${DIR}/output/scores.${split}.jsonl \
    --metrics overall_responsiveness MoverScore_jk \
    --summarizer-type reference \
    --output-file ${DIR}/output/${split}/references/responsiveness_moverscore.json \
    --silent

  python -m sacrerouge correlate \
    --metrics-jsonl-files datasets/duc-tac/tac2008/v1.0/task1.${split}.metrics.jsonl ${DIR}/output/scores.${split}.jsonl \
    --metrics overall_responsiveness MoverScore_jk \
    --summarizer-type all \
    --output-file ${DIR}/output/${split}/all/responsiveness_moverscore.json \
    --silent

  python -m sacrerouge correlate \
    --metrics-jsonl-files datasets/duc-tac/tac2008/v1.0/task1.${split}.metrics.jsonl ${DIR}/output/scores.${split}.jsonl \
    --metrics modified_pyramid_score MoverScore \
    --summarizer-type peer \
    --output-file ${DIR}/output/${split}/peers/pyramid_moverscore.json \
    --silent

  python -m sacrerouge correlate \
    --metrics-jsonl-files datasets/duc-tac/tac2008/v1.0/task1.${split}.metrics.jsonl ${DIR}/output/scores.${split}.jsonl \
    --metrics modified_pyramid_score_jk MoverScore_jk \
    --summarizer-type reference \
    --output-file ${DIR}/output/${split}/references/pyramid_moverscore.json \
    --silent

  python -m sacrerouge correlate \
    --metrics-jsonl-files datasets/duc-tac/tac2008/v1.0/task1.${split}.metrics.jsonl ${DIR}/output/scores.${split}.jsonl \
    --metrics modified_pyramid_score_jk MoverScore_jk \
    --summarizer-type all \
    --output-file ${DIR}/output/${split}/all/pyramid_moverscore.json \
    --silent
done
