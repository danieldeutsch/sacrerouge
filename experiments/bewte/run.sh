DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

input_files=(
  'datasets/duc-tac/duc2005/v1.0/task1.summaries.jsonl'
  'datasets/duc-tac/duc2006/v1.0/task1.summaries.jsonl'
  'datasets/duc-tac/duc2007/v1.0/task1.summaries.jsonl'
  'datasets/duc-tac/tac2008/v1.0/task1.A.summaries.jsonl'
  'datasets/duc-tac/tac2009/v1.0/task1.A.summaries.jsonl'
  'datasets/duc-tac/tac2010/v1.0/task1.A.summaries.jsonl'
  'datasets/duc-tac/tac2011/v1.0/task1.A.summaries.jsonl'
)

metrics_files=(
  'datasets/duc-tac/duc2005/v1.0/task1.metrics.jsonl'
  'datasets/duc-tac/duc2006/v1.0/task1.metrics.jsonl'
  'datasets/duc-tac/duc2007/v1.0/task1.metrics.jsonl'
  'datasets/duc-tac/tac2008/v1.0/task1.A.metrics.jsonl'
  'datasets/duc-tac/tac2009/v1.0/task1.A.metrics.jsonl'
  'datasets/duc-tac/tac2010/v1.0/task1.A.metrics.jsonl'
  'datasets/duc-tac/tac2011/v1.0/task1.A.metrics.jsonl'
)

judgment_metrics=(
  'responsiveness'
  'overall_responsiveness'
  'content_responsiveness'
  'overall_responsiveness'
  'overall_responsiveness'
  'overall_responsiveness'
  'overall_responsiveness'
)

output_dirs=(
  'duc2005'
  'duc2006'
  'duc2007'
  'tac2008'
  'tac2009'
  'tac2010'
  'tac2011'
)

for ((i=0;i<${#input_files[@]};++i)); do
  python -m sacrerouge score \
    ${DIR}/config.jsonnet \
    ${DIR}/output/${output_dirs[i]}/scores.jsonl \
    --overrides '{"dataset_reader.input_jsonl": "'${input_files[i]}'"}' \
    --log-file ${DIR}/output/${output_dirs[i]}/log.log

  for metric in 'precision' 'recall' 'f1'; do
    python -m sacrerouge correlate \
      --metrics-jsonl-files ${metrics_files[i]} ${DIR}/output/${output_dirs[i]}/scores.jsonl \
      --metrics ${judgment_metrics[i]} BEwTE_${metric} \
      --summarizer-type peer \
      --output-file ${DIR}/output/${output_dirs[i]}/correlations/${metric}-peer.json \
      --log-file ${DIR}/output/${output_dirs[i]}/correlations/log.log

    python -m sacrerouge correlate \
      --metrics-jsonl-files ${metrics_files[i]} ${DIR}/output/${output_dirs[i]}/scores.jsonl \
      --metrics ${judgment_metrics[i]} BEwTE_jk_${metric} \
      --summarizer-type all \
      --output-file ${DIR}/output/${output_dirs[i]}/correlations/${metric}-all.json \
      --log-file ${DIR}/output/${output_dirs[i]}/correlations/log.log
  done
done

for summarizer_type in 'all' 'peer'; do
  for level in 'summary_level' 'system_level'; do
    python -m sacrerouge.scripts.create_correlations_table \
      ${DIR}/output/tables/${summarizer_type}-${level}.html \
      ${level} \
      --input ${DIR}/output/duc2005/correlations/precision-${summarizer_type}.json BEwTE-P DUC2005 \
      --input ${DIR}/output/duc2006/correlations/precision-${summarizer_type}.json BEwTE-P DUC2006 \
      --input ${DIR}/output/duc2007/correlations/precision-${summarizer_type}.json BEwTE-P DUC2007 \
      --input ${DIR}/output/tac2008/correlations/precision-${summarizer_type}.json BEwTE-P TAC2008 \
      --input ${DIR}/output/tac2009/correlations/precision-${summarizer_type}.json BEwTE-P TAC2009 \
      --input ${DIR}/output/tac2010/correlations/precision-${summarizer_type}.json BEwTE-P TAC2010 \
      --input ${DIR}/output/tac2011/correlations/precision-${summarizer_type}.json BEwTE-P TAC2011 \
      --input ${DIR}/output/duc2005/correlations/recall-${summarizer_type}.json BEwTE-R DUC2005 \
      --input ${DIR}/output/duc2006/correlations/recall-${summarizer_type}.json BEwTE-R DUC2006 \
      --input ${DIR}/output/duc2007/correlations/recall-${summarizer_type}.json BEwTE-R DUC2007 \
      --input ${DIR}/output/tac2008/correlations/recall-${summarizer_type}.json BEwTE-R TAC2008 \
      --input ${DIR}/output/tac2009/correlations/recall-${summarizer_type}.json BEwTE-R TAC2009 \
      --input ${DIR}/output/tac2010/correlations/recall-${summarizer_type}.json BEwTE-R TAC2010 \
      --input ${DIR}/output/tac2011/correlations/recall-${summarizer_type}.json BEwTE-R TAC2011 \
      --input ${DIR}/output/duc2005/correlations/f1-${summarizer_type}.json BEwTE-F1 DUC2005 \
      --input ${DIR}/output/duc2006/correlations/f1-${summarizer_type}.json BEwTE-F1 DUC2006 \
      --input ${DIR}/output/duc2007/correlations/f1-${summarizer_type}.json BEwTE-F1 DUC2007 \
      --input ${DIR}/output/tac2008/correlations/f1-${summarizer_type}.json BEwTE-F1 TAC2008 \
      --input ${DIR}/output/tac2009/correlations/f1-${summarizer_type}.json BEwTE-F1 TAC2009 \
      --input ${DIR}/output/tac2010/correlations/f1-${summarizer_type}.json BEwTE-F1 TAC2010 \
      --input ${DIR}/output/tac2011/correlations/f1-${summarizer_type}.json BEwTE-F1 TAC2011
  done
done