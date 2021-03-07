DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

for split in 'abs' 'ext' 'mix'; do
    python -m sacrerouge bewte score \
      --input-files datasets/bhandari2020/summaries-${split}.jsonl \
      --dataset-reader reference-based \
      --output-jsonl ${DIR}/output/bhandari2020/scores-${split}.jsonl \
      --log-file ${DIR}/output/bhandari2020/log.log

    for metric in 'precision' 'recall' 'f1'; do
      python -m sacrerouge correlate \
        --metrics-jsonl-files datasets/bhandari2020/metrics-${split}.jsonl ${DIR}/output/bhandari2020/scores-${split}.jsonl \
        --metrics litepyramid_recall BEwTE_${metric} \
        --summarizer-type peer \
        --output-file ${DIR}/output/bhandari2020/correlations/${split}/${metric}-peer.json \
        --log-file ${DIR}/output/bhandari2020/correlations/log.log \
        &
    done
    wait
done

for summarizer_type in 'peer'; do
  for level in 'summary_level' 'system_level'; do
    python -m sacrerouge.scripts.create_correlations_table \
      ${DIR}/output/tables/bhandari2020/${summarizer_type}-${level}.html \
      ${level} \
      --input ${DIR}/output/bhandari2020/correlations/abs/precision-${summarizer_type}.json BEwTE-P Bhandari2020-Abs \
      --input ${DIR}/output/bhandari2020/correlations/abs/recall-${summarizer_type}.json BEwTE-R Bhandari2020-Abs \
      --input ${DIR}/output/bhandari2020/correlations/abs/f1-${summarizer_type}.json BEwTE-F1 Bhandari2020-Abs \
      --input ${DIR}/output/bhandari2020/correlations/ext/precision-${summarizer_type}.json BEwTE-P Bhandari2020-Ext \
      --input ${DIR}/output/bhandari2020/correlations/ext/recall-${summarizer_type}.json BEwTE-R Bhandari2020-Ext \
      --input ${DIR}/output/bhandari2020/correlations/ext/f1-${summarizer_type}.json BEwTE-F1 Bhandari2020-Ext \
      --input ${DIR}/output/bhandari2020/correlations/mix/precision-${summarizer_type}.json BEwTE-P Bhandari2020-Mix \
      --input ${DIR}/output/bhandari2020/correlations/mix/recall-${summarizer_type}.json BEwTE-R Bhandari2020-Mix \
      --input ${DIR}/output/bhandari2020/correlations/mix/f1-${summarizer_type}.json BEwTE-F1 Bhandari2020-Mix
  done
done