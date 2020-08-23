DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

for dataset in 'tac2008' 'tac2009' 'tac2010' 'tac2011'; do
  for checkpoint in bleurt-base-128 bleurt-large-512; do
    python -m sacrerouge bleurt score \
      ${DIR}/output/${dataset}/${checkpoint}/scores.jsonl \
      --input-files datasets/duc-tac/${dataset}/v1.0/task1.A.summaries.jsonl \
      --dataset-reader reference-based \
      --environment_name /shared/ddeutsch/envs/tf \
      --checkpoint ${checkpoint} \
      --log-file ${DIR}/output/${dataset}/${checkpoint}/log.log

    for metric in 'average' 'max'; do
      python -m sacrerouge correlate \
        --metrics-jsonl-files datasets/duc-tac/${dataset}/v1.0/task1.A.metrics.jsonl ${DIR}/output/${dataset}/${checkpoint}/scores.jsonl \
        --metrics overall_responsiveness bleurt_${metric} \
        --summarizer-type peer \
        --output-file ${DIR}/output/${dataset}/${checkpoint}/correlations/${metric}-peer.json \
        --log-file ${DIR}/output/${dataset}/${checkpoint}/correlations/log.log

      python -m sacrerouge correlate \
        --metrics-jsonl-files datasets/duc-tac/${dataset}/v1.0/task1.A.metrics.jsonl ${DIR}/output/${dataset}/${checkpoint}/scores.jsonl \
        --metrics overall_responsiveness bleurt_jk_${metric} \
        --summarizer-type all \
        --output-file ${DIR}/output/${dataset}/${checkpoint}/correlations/${metric}-all.json \
        --log-file ${DIR}/output/${dataset}/${checkpoint}/correlations/log.log
    done
  done
done

for summarizer_type in 'all' 'peer'; do
  for level in 'summary_level' 'system_level'; do
    python -m sacrerouge.scripts.create_correlations_table \
      ${DIR}/output/tables/${summarizer_type}-${level}.html \
      ${level} \
      --input ${DIR}/output/tac2008/bleurt-base-128/correlations/average-${summarizer_type}.json BLEURT-Base-128-Avg TAC2008 \
      --input ${DIR}/output/tac2009/bleurt-base-128/correlations/average-${summarizer_type}.json BLEURT-Base-128-Avg TAC2009 \
      --input ${DIR}/output/tac2010/bleurt-base-128/correlations/average-${summarizer_type}.json BLEURT-Base-128-Avg TAC2010 \
      --input ${DIR}/output/tac2011/bleurt-base-128/correlations/average-${summarizer_type}.json BLEURT-Base-128-Avg TAC2011 \
      --input ${DIR}/output/tac2008/bleurt-base-128/correlations/max-${summarizer_type}.json BLEURT-Base-128-Max TAC2008 \
      --input ${DIR}/output/tac2009/bleurt-base-128/correlations/max-${summarizer_type}.json BLEURT-Base-128-Max TAC2009 \
      --input ${DIR}/output/tac2010/bleurt-base-128/correlations/max-${summarizer_type}.json BLEURT-Base-128-Max TAC2010 \
      --input ${DIR}/output/tac2011/bleurt-base-128/correlations/max-${summarizer_type}.json BLEURT-Base-128-Max TAC2011 \
      --input ${DIR}/output/tac2008/bleurt-large-512/correlations/average-${summarizer_type}.json BLEURT-Large-512-Avg TAC2008 \
      --input ${DIR}/output/tac2009/bleurt-large-512/correlations/average-${summarizer_type}.json BLEURT-Large-512-Avg TAC2009 \
      --input ${DIR}/output/tac2010/bleurt-large-512/correlations/average-${summarizer_type}.json BLEURT-Large-512-Avg TAC2010 \
      --input ${DIR}/output/tac2011/bleurt-large-512/correlations/average-${summarizer_type}.json BLEURT-Large-512-Avg TAC2011 \
      --input ${DIR}/output/tac2008/bleurt-large-512/correlations/max-${summarizer_type}.json BLEURT-Large-512-Max TAC2008 \
      --input ${DIR}/output/tac2009/bleurt-large-512/correlations/max-${summarizer_type}.json BLEURT-Large-512-Max TAC2009 \
      --input ${DIR}/output/tac2010/bleurt-large-512/correlations/max-${summarizer_type}.json BLEURT-Large-512-Max TAC2010 \
      --input ${DIR}/output/tac2011/bleurt-large-512/correlations/max-${summarizer_type}.json BLEURT-Large-512-Max TAC2011
  done
done