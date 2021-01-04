DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

for dataset in 'tac2008' 'tac2009' 'tac2010' 'tac2011'; do
  python -m sacrerouge rouge score \
    --input-files datasets/duc-tac/${dataset}/v1.0/task1.A.summaries.jsonl \
    --dataset-reader reference-based \
    --output-jsonl ${DIR}/output/${dataset}/scores.jsonl \
    --compute_rouge_l true \
    --skip_bigram_gap_length 4

  for metric in 'rouge-1' 'rouge-2' 'rouge-l' 'rouge-su4'; do
    for submetric in 'precision' 'recall' 'f1'; do
      python -m sacrerouge correlate \
      --metrics-jsonl-files datasets/duc-tac/${dataset}/v1.0/task1.A.metrics.jsonl ${DIR}/output/${dataset}/scores.jsonl \
      --metrics overall_responsiveness ${metric}_${submetric} \
      --summarizer-type peer \
      --output-file ${DIR}/output/${dataset}/correlations/${metric}-${submetric}-peer.json \
      --log-file ${DIR}/output/${dataset}/correlations/log.log \
      --silent \
      &

      python -m sacrerouge correlate \
        --metrics-jsonl-files datasets/duc-tac/${dataset}/v1.0/task1.A.metrics.jsonl ${DIR}/output/${dataset}/scores.jsonl \
        --metrics overall_responsiveness ${metric}_jk_${submetric} \
        --summarizer-type all \
        --output-file ${DIR}/output/${dataset}/correlations/${metric}-${submetric}-all.json \
        --log-file ${DIR}/output/${dataset}/correlations/log.log \
        --silent \
        &
    done
  done
  wait
done

for summarizer_type in 'all' 'peer'; do
  for level in 'summary_level' 'system_level'; do
    python -m sacrerouge.scripts.create_correlations_table \
      ${DIR}/output/tables/${summarizer_type}-${level}.html \
      ${level} \
      --input ${DIR}/output/tac2008/correlations/rouge-1-precision-${summarizer_type}.json R1-P TAC2008 \
      --input ${DIR}/output/tac2009/correlations/rouge-1-precision-${summarizer_type}.json R1-P TAC2009 \
      --input ${DIR}/output/tac2010/correlations/rouge-1-precision-${summarizer_type}.json R1-P TAC2010 \
      --input ${DIR}/output/tac2011/correlations/rouge-1-precision-${summarizer_type}.json R1-P TAC2011 \
      --input ${DIR}/output/tac2008/correlations/rouge-1-recall-${summarizer_type}.json R1-R TAC2008 \
      --input ${DIR}/output/tac2009/correlations/rouge-1-recall-${summarizer_type}.json R1-R TAC2009 \
      --input ${DIR}/output/tac2010/correlations/rouge-1-recall-${summarizer_type}.json R1-R TAC2010 \
      --input ${DIR}/output/tac2011/correlations/rouge-1-recall-${summarizer_type}.json R1-R TAC2011 \
      --input ${DIR}/output/tac2008/correlations/rouge-1-f1-${summarizer_type}.json R1-F1 TAC2008 \
      --input ${DIR}/output/tac2009/correlations/rouge-1-f1-${summarizer_type}.json R1-F1 TAC2009 \
      --input ${DIR}/output/tac2010/correlations/rouge-1-f1-${summarizer_type}.json R1-F1 TAC2010 \
      --input ${DIR}/output/tac2011/correlations/rouge-1-f1-${summarizer_type}.json R1-F1 TAC2011 \
      --input ${DIR}/output/tac2008/correlations/rouge-2-precision-${summarizer_type}.json R2-P TAC2008 \
      --input ${DIR}/output/tac2009/correlations/rouge-2-precision-${summarizer_type}.json R2-P TAC2009 \
      --input ${DIR}/output/tac2010/correlations/rouge-2-precision-${summarizer_type}.json R2-P TAC2010 \
      --input ${DIR}/output/tac2011/correlations/rouge-2-precision-${summarizer_type}.json R2-P TAC2011 \
      --input ${DIR}/output/tac2008/correlations/rouge-2-recall-${summarizer_type}.json R2-R TAC2008 \
      --input ${DIR}/output/tac2009/correlations/rouge-2-recall-${summarizer_type}.json R2-R TAC2009 \
      --input ${DIR}/output/tac2010/correlations/rouge-2-recall-${summarizer_type}.json R2-R TAC2010 \
      --input ${DIR}/output/tac2011/correlations/rouge-2-recall-${summarizer_type}.json R2-R TAC2011 \
      --input ${DIR}/output/tac2008/correlations/rouge-2-f1-${summarizer_type}.json R2-F1 TAC2008 \
      --input ${DIR}/output/tac2009/correlations/rouge-2-f1-${summarizer_type}.json R2-F1 TAC2009 \
      --input ${DIR}/output/tac2010/correlations/rouge-2-f1-${summarizer_type}.json R2-F1 TAC2010 \
      --input ${DIR}/output/tac2011/correlations/rouge-2-f1-${summarizer_type}.json R2-F1 TAC2011 \
      --input ${DIR}/output/tac2008/correlations/rouge-l-precision-${summarizer_type}.json RL-P TAC2008 \
      --input ${DIR}/output/tac2009/correlations/rouge-l-precision-${summarizer_type}.json RL-P TAC2009 \
      --input ${DIR}/output/tac2010/correlations/rouge-l-precision-${summarizer_type}.json RL-P TAC2010 \
      --input ${DIR}/output/tac2011/correlations/rouge-l-precision-${summarizer_type}.json RL-P TAC2011 \
      --input ${DIR}/output/tac2008/correlations/rouge-l-recall-${summarizer_type}.json RL-R TAC2008 \
      --input ${DIR}/output/tac2009/correlations/rouge-l-recall-${summarizer_type}.json RL-R TAC2009 \
      --input ${DIR}/output/tac2010/correlations/rouge-l-recall-${summarizer_type}.json RL-R TAC2010 \
      --input ${DIR}/output/tac2011/correlations/rouge-l-recall-${summarizer_type}.json RL-R TAC2011 \
      --input ${DIR}/output/tac2008/correlations/rouge-l-f1-${summarizer_type}.json RL-F1 TAC2008 \
      --input ${DIR}/output/tac2009/correlations/rouge-l-f1-${summarizer_type}.json RL-F1 TAC2009 \
      --input ${DIR}/output/tac2010/correlations/rouge-l-f1-${summarizer_type}.json RL-F1 TAC2010 \
      --input ${DIR}/output/tac2011/correlations/rouge-l-f1-${summarizer_type}.json RL-F1 TAC2011 \
      --input ${DIR}/output/tac2008/correlations/rouge-su4-precision-${summarizer_type}.json RSU4-P TAC2008 \
      --input ${DIR}/output/tac2009/correlations/rouge-su4-precision-${summarizer_type}.json RSU4-P TAC2009 \
      --input ${DIR}/output/tac2010/correlations/rouge-su4-precision-${summarizer_type}.json RSU4-P TAC2010 \
      --input ${DIR}/output/tac2011/correlations/rouge-su4-precision-${summarizer_type}.json RSU4-P TAC2011 \
      --input ${DIR}/output/tac2008/correlations/rouge-su4-recall-${summarizer_type}.json RSU4-R TAC2008 \
      --input ${DIR}/output/tac2009/correlations/rouge-su4-recall-${summarizer_type}.json RSU4-R TAC2009 \
      --input ${DIR}/output/tac2010/correlations/rouge-su4-recall-${summarizer_type}.json RSU4-R TAC2010 \
      --input ${DIR}/output/tac2011/correlations/rouge-su4-recall-${summarizer_type}.json RSU4-R TAC2011 \
      --input ${DIR}/output/tac2008/correlations/rouge-su4-f1-${summarizer_type}.json RSU4-F1 TAC2008 \
      --input ${DIR}/output/tac2009/correlations/rouge-su4-f1-${summarizer_type}.json RSU4-F1 TAC2009 \
      --input ${DIR}/output/tac2010/correlations/rouge-su4-f1-${summarizer_type}.json RSU4-F1 TAC2010 \
      --input ${DIR}/output/tac2011/correlations/rouge-su4-f1-${summarizer_type}.json RSU4-F1 TAC2011
  done
done