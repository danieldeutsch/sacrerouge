DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

for dataset in 'tac2008' 'tac2009' 'tac2010' 'tac2011'; do
  python -m sacrerouge score \
    ${DIR}/config.jsonnet \
    ${DIR}/output/${dataset}/scores.jsonl \
    --overrides '{"input_files": ["datasets/duc-tac/'"${dataset}"'/v1.0/task1.A.summaries.jsonl"]}' \
    --log-file ${DIR}/output/${dataset}/log.log

  for metric in 'AutoSummENG' 'MeMoG' 'NPowER'; do
    python -m sacrerouge correlate \
      --metrics-jsonl-files datasets/duc-tac/${dataset}/v1.0/task1.A.metrics.jsonl ${DIR}/output/${dataset}/scores.jsonl \
      --metrics overall_responsiveness ${metric} \
      --summarizer-type peer \
      --output-file ${DIR}/output/${dataset}/correlations/${metric}-peer.json \
      --log-file ${DIR}/output/${dataset}/correlations/log.log

    python -m sacrerouge correlate \
      --metrics-jsonl-files datasets/duc-tac/${dataset}/v1.0/task1.A.metrics.jsonl ${DIR}/output/${dataset}/scores.jsonl \
      --metrics overall_responsiveness ${metric}_jk \
      --summarizer-type all \
      --output-file ${DIR}/output/${dataset}/correlations/${metric}-all.json \
      --log-file ${DIR}/output/${dataset}/correlations/log.log
  done
done

for summarizer_type in 'all' 'peer'; do
  for level in 'summary_level' 'system_level'; do
    python -m sacrerouge.scripts.create_correlations_table \
      ${DIR}/output/tables/${summarizer_type}-${level}.html \
      ${level} \
      --input ${DIR}/output/tac2008/correlations/AutoSummENG-${summarizer_type}.json AutoSummENG TAC2008 \
      --input ${DIR}/output/tac2009/correlations/AutoSummENG-${summarizer_type}.json AutoSummENG TAC2009 \
      --input ${DIR}/output/tac2010/correlations/AutoSummENG-${summarizer_type}.json AutoSummENG TAC2010 \
      --input ${DIR}/output/tac2011/correlations/AutoSummENG-${summarizer_type}.json AutoSummENG TAC2011 \
      --input ${DIR}/output/tac2008/correlations/MeMoG-${summarizer_type}.json MeMoG TAC2008 \
      --input ${DIR}/output/tac2009/correlations/MeMoG-${summarizer_type}.json MeMoG TAC2009 \
      --input ${DIR}/output/tac2010/correlations/MeMoG-${summarizer_type}.json MeMoG TAC2010 \
      --input ${DIR}/output/tac2011/correlations/MeMoG-${summarizer_type}.json MeMoG TAC2011 \
      --input ${DIR}/output/tac2008/correlations/NPowER-${summarizer_type}.json NPowER TAC2008 \
      --input ${DIR}/output/tac2009/correlations/NPowER-${summarizer_type}.json NPowER TAC2009 \
      --input ${DIR}/output/tac2010/correlations/NPowER-${summarizer_type}.json NPowER TAC2010 \
      --input ${DIR}/output/tac2011/correlations/NPowER-${summarizer_type}.json NPowER TAC2011
  done
done