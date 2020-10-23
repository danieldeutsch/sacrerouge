DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

for dataset in 'tac2008' 'tac2009' 'tac2010' 'tac2011'; do
  python -m sacrerouge decomposed-rouge score \
    ${DIR}/output/${dataset}/scores.jsonl \
    --input-files datasets/duc-tac/${dataset}/v1.0/task1.A.summaries.jsonl \
    --dataset-reader reference-based \
    --log-file ${DIR}/output/${dataset}/log.log

  for metric in rouge-1 ner pos-adj pos-verb pos-noun pos-propn pos-adv pos-num dep-root dep-nsubj dep-dobj np-chunks dep-verb+nsubj dep-verb+dobj dep-verb+nsubj+dobj stopwords; do
    python -m sacrerouge correlate \
      --metrics-jsonl-files datasets/duc-tac/${dataset}/v1.0/task1.A.metrics.jsonl ${DIR}/output/${dataset}/scores.jsonl \
      --metrics overall_responsiveness decomposed-rouge_${metric}_recall \
      --summarizer-type peer \
      --output-file ${DIR}/output/${dataset}/correlations/${metric}-peer.json \
      --log-file ${DIR}/output/${dataset}/correlations/log.log

    python -m sacrerouge correlate \
      --metrics-jsonl-files datasets/duc-tac/${dataset}/v1.0/task1.A.metrics.jsonl ${DIR}/output/${dataset}/scores.jsonl \
      --metrics overall_responsiveness decomposed-rouge_jk_${metric}_recall \
      --summarizer-type all \
      --output-file ${DIR}/output/${dataset}/correlations/${metric}-all.json \
      --log-file ${DIR}/output/${dataset}/correlations/log.log
  done
done

for summarizer_type in 'all' 'peer'; do
  for level in 'summary_level' 'system_level'; do
    python ${DIR}/create_correlations_table.py \
      --dataset-names TAC2008 TAC2009 TAC2010 TAC2011 \
      --correlation-dirs ${DIR}/output/tac2008/correlations ${DIR}/output/tac2009/correlations ${DIR}/output/tac2010/correlations ${DIR}/output/tac2011/correlations \
      --output-file ${DIR}/output/tables/${summarizer_type}-${level}.html \
      --correlation-level ${level} \
      --summarizer-type ${summarizer_type}
  done
done

python ${DIR}/create_contribution_table.py \
  --dataset-names TAC2008 TAC2009 TAC2010 TAC2011 \
  --score-jsonls ${DIR}/output/tac2008/scores.jsonl ${DIR}/output/tac2009/scores.jsonl ${DIR}/output/tac2010/scores.jsonl ${DIR}/output/tac2011/scores.jsonl \
  --output-file ${DIR}/output/tables/contributions.html
