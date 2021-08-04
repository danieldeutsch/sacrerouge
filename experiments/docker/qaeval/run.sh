DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
set -e

DEVICE=1
CONDA_INIT="/home1/d/ddeutsch/miniconda3/etc/profile.d/conda.sh"
ORIG_ENV="/shared/ddeutsch/envs/sr-qaeval"
DOCKER_ENV="/shared/ddeutsch/envs/sr-docker"
datasets=( 'tac2008' 'fabbri2020' 'bhandari2020' )
input_files=( "datasets/duc-tac/tac2008/v1.0/task1.A.summaries.jsonl" "datasets/fabbri2020/summaries.jsonl" "datasets/bhandari2020/summaries-mix.jsonl" )

source ${CONDA_INIT}

for i in "${!datasets[@]}"; do
  dataset="${datasets[i]}"
  input_file="${input_files[i]}"

  conda activate ${ORIG_ENV}

  python -m sacrerouge qa-eval score \
    --input-files ${input_file} \
    --dataset-reader reference-based \
    --output-jsonl ${DIR}/output/${dataset}/original-scores.jsonl \
    --use_lerc true \
    --cuda_device ${DEVICE}

  conda deactivate
  conda activate ${DOCKER_ENV}

  python -m sacrerouge docker-qa-eval score \
    --input-files ${input_file} \
    --dataset-reader reference-based \
    --output-jsonl ${DIR}/output/${dataset}/docker-scores.jsonl \
    --device ${DEVICE}

  conda deactivate
done

conda activate ${ORIG_ENV}

for i in "${!datasets[@]}"; do
  dataset="${datasets[i]}"
  python ${DIR}/../compare.py \
    --original ${DIR}/output/${dataset}/original-scores.jsonl \
    --docker ${DIR}/output/${dataset}/docker-scores.jsonl
done