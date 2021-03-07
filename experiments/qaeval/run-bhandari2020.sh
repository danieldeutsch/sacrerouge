DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

for split in 'abs' 'ext'; do
    python -m sacrerouge qa-eval score \
        --input-files datasets/bhandari2020/summaries-${split}.jsonl \
        --dataset-reader reference-based \
        --output-jsonl ${DIR}/output/bhandari2020/scores-${split}.jsonl \
        --log-file ${DIR}/output/bhandari2020/${split}/log.log \
        --use_lerc true
done
cat ${DIR}/output/bhandari2020/scores-abs.jsonl ${DIR}/output/bhandari2020/scores-ext.jsonl > ${DIR}/output/bhandari2020/scores-mix.jsonl


for split in 'abs' 'ext' 'mix'; do
    for metric in 'em' 'f1' 'lerc'; do
      python -m sacrerouge correlate \
        --metrics-jsonl-files datasets/bhandari2020/metrics-${split}.jsonl ${DIR}/output/bhandari2020/scores-${split}.jsonl \
        --metrics litepyramid_recall qa-eval_${metric} \
        --summarizer-type peer \
        --output-file ${DIR}/output/bhandari2020/correlations/${split}/${metric}-peer.json \
        --log-file ${DIR}/output/bhandari2020/correlations/${split}/log.log
    done
done

for summarizer_type in 'peer'; do
  for level in 'summary_level' 'system_level'; do
    python -m sacrerouge.scripts.create_correlations_table \
      ${DIR}/output/tables/bhandari2020/${summarizer_type}-${level}.html \
      ${level} \
      --input ${DIR}/output/bhandari2020/correlations/abs/em-${summarizer_type}.json QA-EM Bhandari2020-Abs \
      --input ${DIR}/output/bhandari2020/correlations/abs/f1-${summarizer_type}.json QA-F1 Bhandari2020-Abs \
      --input ${DIR}/output/bhandari2020/correlations/abs/lerc-${summarizer_type}.json QA-LERC Bhandari2020-Abs \
      --input ${DIR}/output/bhandari2020/correlations/ext/em-${summarizer_type}.json QA-EM Bhandari2020-Ext \
      --input ${DIR}/output/bhandari2020/correlations/ext/f1-${summarizer_type}.json QA-F1 Bhandari2020-Ext \
      --input ${DIR}/output/bhandari2020/correlations/ext/lerc-${summarizer_type}.json QA-LERC Bhandari2020-Ext \
      --input ${DIR}/output/bhandari2020/correlations/mix/em-${summarizer_type}.json QA-EM Bhandari2020-Mix \
      --input ${DIR}/output/bhandari2020/correlations/mix/f1-${summarizer_type}.json QA-F1 Bhandari2020-Mix \
      --input ${DIR}/output/bhandari2020/correlations/mix/lerc-${summarizer_type}.json QA-LERC Bhandari2020-Mix
  done
done