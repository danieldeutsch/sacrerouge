DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
set -e
source ~/miniconda3/etc/profile.d/conda.sh

# Run truecasing
conda deactivate
conda activate /shared/ddeutsch/envs/truecaser

python ${DIR}/truecaser.py \
  --input-jsonl datasets/fabbri2020/summaries.jsonl \
  --output-jsonl ${DIR}/output/fabbri2020/summaries-truecased.jsonl

conda deactivate

python -m sacrerouge apes score \
  --input-files datasets/fabbri2020/summaries.jsonl \
  --dataset-reader reference-based \
  --output-jsonl ${DIR}/output/fabbri2020/scores-default.jsonl \
  --verbose true \
  --environment_name /shared/ddeutsch/envs/apes

python -m sacrerouge apes score \
  --input-files ${DIR}/output/fabbri2020/summaries-truecased.jsonl \
  --dataset-reader reference-based \
  --output-jsonl ${DIR}/output/fabbri2020/scores-truecased.jsonl \
  --verbose true \
  --environment_name /shared/ddeutsch/envs/apes

for split in default truecased; do
  python -m sacrerouge correlate \
    --metrics-jsonl-files datasets/fabbri2020/metrics.jsonl ${DIR}/output/fabbri2020/scores-${split}.jsonl \
    --metrics expert_relevance APES \
    --summarizer-type peer \
    --output-file ${DIR}/output/fabbri2020/correlations/peer-${split}.json
done

for summarizer_type in 'peer'; do
  for level in 'summary_level' 'system_level'; do
    python -m sacrerouge.scripts.create_correlations_table \
      ${DIR}/output/tables/fabbri2020-${summarizer_type}-${level}.html \
      ${level} \
      --input ${DIR}/output/fabbri2020/correlations/${summarizer_type}-default.json APES Fabbri2020 \
      --input ${DIR}/output/fabbri2020/correlations/${summarizer_type}-truecased.json APES-Truecased Fabbri2020
  done
done