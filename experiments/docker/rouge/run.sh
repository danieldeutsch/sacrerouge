DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
set -e

datasets=( 'tac2008' 'fabbri2020' 'bhandari2020' )
input_files=( "datasets/duc-tac/tac2008/v1.0/task1.A.summaries.jsonl" "datasets/fabbri2020/summaries.jsonl" "datasets/bhandari2020/summaries-mix.jsonl" )

for i in "${!datasets[@]}"; do
  dataset="${datasets[i]}"
  input_file="${input_files[i]}"

  python -m sacrerouge rouge score \
    --input-files ${input_file} \
    --dataset-reader reference-based \
    --output-jsonl ${DIR}/output/${dataset}/original-scores.jsonl \
    --compute_rouge_l true \
    --skip_bigram_gap_length 4

  python -m sacrerouge docker-rouge score \
    --input-files ${input_file} \
    --dataset-reader reference-based \
    --sentence_split false \
    --output-jsonl ${DIR}/output/${dataset}/docker-scores.jsonl
done

for i in "${!datasets[@]}"; do
  dataset="${datasets[i]}"
  python ${DIR}/../compare.py \
    --original ${DIR}/output/${dataset}/original-scores.jsonl \
    --docker ${DIR}/output/${dataset}/docker-scores.jsonl
done