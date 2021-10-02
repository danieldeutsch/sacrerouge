DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
set -e

datasets=( 'tac2008' 'fabbri2020' 'bhandari2020' )
summary_files=( "datasets/duc-tac/tac2008/v1.0/task1.A.summaries.jsonl" "datasets/fabbri2020/summaries.jsonl" "datasets/bhandari2020/summaries-mix.jsonl" )
metrics_files=( "datasets/duc-tac/tac2008/v1.0/task1.A.metrics.jsonl" "datasets/fabbri2020/metrics.jsonl" "datasets/bhandari2020/metrics-mix.jsonl" )
ground_truths=( "overall_responsiveness" "expert_relevance" "litepyramid_recall" )

for i in "${!datasets[@]}"; do
  dataset="${datasets[i]}"
  input_file="${summary_files[i]}"
  metrics_file="${metrics_files[i]}"
  ground_truth="${ground_truths[i]}"

#  python -m sacrerouge docker-moverscore score \
#    --input-files ${input_file} \
#    --dataset-reader reference-based \
#    --output-jsonl ${DIR}/output/${dataset}/docker-scores.jsonl

  python -m sacrerouge correlate \
    --metrics-jsonl-files ${metrics_file} ${DIR}/output/${dataset}/docker-scores.jsonl \
    --metrics ${ground_truth} moverscore \
    --summarizer-type peer \
    --output-file ${DIR}/output/${dataset}/correlations.json
done