DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

for split in 'abs' 'ext'; do
    python -m sacrerouge sent-bleu score \
        --input-files datasets/bhandari2020/summaries-${split}.jsonl \
        --dataset-reader reference-based \
        --output-jsonl ${DIR}/output/bhandari2020/scores-${split}.jsonl \
        --log-file ${DIR}/output/bhandari2020/${split}/log.log
done
cat ${DIR}/output/bhandari2020/scores-abs.jsonl ${DIR}/output/bhandari2020/scores-ext.jsonl > ${DIR}/output/bhandari2020/scores-mix.jsonl


for split in 'abs' 'ext' 'mix'; do
    python -m sacrerouge correlate \
        --metrics-jsonl-files datasets/bhandari2020/metrics-${split}.jsonl ${DIR}/output/bhandari2020/scores-${split}.jsonl \
        --metrics litepyramid_recall sent-bleu \
        --summarizer-type peer \
        --output-file ${DIR}/output/bhandari2020/correlations/${split}.json \
        --log-file ${DIR}/output/bhandari2020/correlations/${split}-log.log
done

for level in 'summary_level' 'system_level'; do
python -m sacrerouge.scripts.create_correlations_table \
  ${DIR}/output/tables/bhandari2020-${level}.html \
  ${level} \
  --input ${DIR}/output/bhandari2020/correlations/abs.json SentBLEU Bhandari2020-Abs \
  --input ${DIR}/output/bhandari2020/correlations/ext.json SentBLEU Bhandari2020-Ext \
  --input ${DIR}/output/bhandari2020/correlations/mix.json SentBLEU Bhandari2020-Mix
done
