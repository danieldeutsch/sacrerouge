DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

datasets=(
  'duc2005'
  'duc2006'
  'duc2007'
)

model_files=(
  "${SACREROUGE_DATA_ROOT}/metrics/SumQE/models/multitask_5-duc2006_duc2007.npy"
  "${SACREROUGE_DATA_ROOT}/metrics/SumQE/models/multitask_5-duc2005_duc2007.npy"
  "${SACREROUGE_DATA_ROOT}/metrics/SumQE/models/multitask_5-duc2005_duc2006.npy"
)

for ((i=0;i<${#datasets[@]};++i)); do
  MODEL_FILE=${model_files[i]} python -m sacrerouge score \
    ${DIR}/config.jsonnet \
    ${DIR}/output/${datasets[i]}/scores.jsonl \
    --overrides '{"input_files": ["datasets/duc-tac/'"${datasets[i]}"'/v1.0/task1.summaries.jsonl"]}' \
    --log-file ${DIR}/output/${datasets[i]}/log.log

  for q in 'Q1' 'Q2' 'Q3' 'Q4' 'Q5'; do
    for summarizer_type in 'all' 'peer'; do
      python -m sacrerouge correlate \
        --metrics-jsonl-files datasets/duc-tac/${datasets[i]}/v1.0/task1.metrics.jsonl ${DIR}/output/${datasets[i]}/scores.jsonl \
        --metrics linguistic_quality_${q} SumQE_${q} \
        --summarizer-type ${summarizer_type} \
        --output-file ${DIR}/output/${datasets[i]}/correlations/${q}-${summarizer_type}.json \
        --log-file ${DIR}/output/${datasets[i]}/correlations/log.log
    done
  done
done

for summarizer_type in 'all' 'peer'; do
  for level in 'summary_level' 'system_level'; do
    python -m sacrerouge.scripts.create_correlations_table \
      ${DIR}/output/tables/${summarizer_type}-${level}.html \
      ${level} \
      --input ${DIR}/output/duc2005/correlations/Q1-${summarizer_type}.json SumQE DUC2005-Q1 \
      --input ${DIR}/output/duc2006/correlations/Q1-${summarizer_type}.json SumQE DUC2006-Q1 \
      --input ${DIR}/output/duc2007/correlations/Q1-${summarizer_type}.json SumQE DUC2007-Q1 \
      --input ${DIR}/output/duc2005/correlations/Q2-${summarizer_type}.json SumQE DUC2005-Q2 \
      --input ${DIR}/output/duc2006/correlations/Q2-${summarizer_type}.json SumQE DUC2006-Q2 \
      --input ${DIR}/output/duc2007/correlations/Q2-${summarizer_type}.json SumQE DUC2007-Q2 \
      --input ${DIR}/output/duc2005/correlations/Q3-${summarizer_type}.json SumQE DUC2005-Q3 \
      --input ${DIR}/output/duc2006/correlations/Q3-${summarizer_type}.json SumQE DUC2006-Q3 \
      --input ${DIR}/output/duc2007/correlations/Q3-${summarizer_type}.json SumQE DUC2007-Q3 \
      --input ${DIR}/output/duc2005/correlations/Q4-${summarizer_type}.json SumQE DUC2005-Q4 \
      --input ${DIR}/output/duc2006/correlations/Q4-${summarizer_type}.json SumQE DUC2006-Q4 \
      --input ${DIR}/output/duc2007/correlations/Q4-${summarizer_type}.json SumQE DUC2007-Q4 \
      --input ${DIR}/output/duc2005/correlations/Q5-${summarizer_type}.json SumQE DUC2005-Q5 \
      --input ${DIR}/output/duc2006/correlations/Q5-${summarizer_type}.json SumQE DUC2006-Q5 \
      --input ${DIR}/output/duc2007/correlations/Q5-${summarizer_type}.json SumQE DUC2007-Q5
  done
done