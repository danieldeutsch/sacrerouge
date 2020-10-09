DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

for reference in 'single-reference' 'multi-reference'; do
  for level in 'summary_level' 'system_level'; do
    python -m sacrerouge.scripts.create_correlations_table \
      ${DIR}/output/tables/${reference}/${level}.html \
      ${level} \
      --input ${DIR}/output/${reference}/correlations/rouge-1/precision.json R1-P Fabbri2020 \
      --input ${DIR}/output/${reference}/correlations/rouge-1/recall.json R1-R Fabbri2020 \
      --input ${DIR}/output/${reference}/correlations/rouge-1/f1.json R1-F1 Fabbri2020 \
      --input ${DIR}/output/${reference}/correlations/rouge-2/precision.json R2-P Fabbri2020 \
      --input ${DIR}/output/${reference}/correlations/rouge-2/recall.json R2-R Fabbri2020 \
      --input ${DIR}/output/${reference}/correlations/rouge-2/f1.json R2-F1 Fabbri2020 \
      --input ${DIR}/output/${reference}/correlations/bertscore/precision.json BERTScore-P Fabbri2020 \
      --input ${DIR}/output/${reference}/correlations/bertscore/recall.json BERTScore-R Fabbri2020 \
      --input ${DIR}/output/${reference}/correlations/bertscore/f1.json BERTScore-F1 Fabbri2020 \
      --input ${DIR}/output/${reference}/correlations/moverscore.json MoverScore Fabbri2020 \
      --input ${DIR}/output/${reference}/correlations/qaeval/em.json QAEval-EM Fabbri2020 \
      --input ${DIR}/output/${reference}/correlations/qaeval/f1.json QAEval-F1 Fabbri2020
  done
done