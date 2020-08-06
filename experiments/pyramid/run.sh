DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

for dataset in 'tac2008' 'tac2009' 'tac2010' 'tac2011'; do
  python -m sacrerouge pyramid-score score \
    ${DIR}/output/${dataset}/scores.jsonl \
    --input-files datasets/duc-tac/${dataset}/v1.0/task1.A.pyramids.jsonl datasets/duc-tac/${dataset}/v1.0/task1.A.pyramid-annotations.jsonl \
    --name_override sr_modified_pyramid_score \
    --dataset-reader pyramid-based \
    --log-file ${DIR}/output/${dataset}/log.log

  python -m sacrerouge correlate \
    --metrics-jsonl-files datasets/duc-tac/${dataset}/v1.0/task1.A.metrics.jsonl ${DIR}/output/${dataset}/scores.jsonl \
    --metrics overall_responsiveness sr_modified_pyramid_score \
    --summarizer-type peer \
    --output-file ${DIR}/output/${dataset}/correlations/responsiveness-peer.json \
    --log-file ${DIR}/output/${dataset}/correlations/log.log

  python -m sacrerouge correlate \
    --metrics-jsonl-files datasets/duc-tac/${dataset}/v1.0/task1.A.metrics.jsonl ${DIR}/output/${dataset}/scores.jsonl \
    --metrics overall_responsiveness sr_modified_pyramid_score_jk \
    --summarizer-type all \
    --output-file ${DIR}/output/${dataset}/correlations/responsiveness-all.json \
    --log-file ${DIR}/output/${dataset}/correlations/log.log

  python -m sacrerouge correlate \
    --metrics-jsonl-files datasets/duc-tac/${dataset}/v1.0/task1.A.metrics.jsonl ${DIR}/output/${dataset}/scores.jsonl \
    --metrics modified_pyramid_score sr_modified_pyramid_score \
    --summarizer-type peer \
    --output-file ${DIR}/output/${dataset}/correlations/pyramid-peer.json \
    --log-file ${DIR}/output/${dataset}/correlations/log.log

  python -m sacrerouge correlate \
    --metrics-jsonl-files datasets/duc-tac/${dataset}/v1.0/task1.A.metrics.jsonl ${DIR}/output/${dataset}/scores.jsonl \
    --metrics modified_pyramid_score_jk sr_modified_pyramid_score_jk \
    --summarizer-type all \
    --output-file ${DIR}/output/${dataset}/correlations/pyramid-all.json \
    --log-file ${DIR}/output/${dataset}/correlations/log.log
done

for metric in 'responsiveness' 'pyramid'; do
  for summarizer_type in 'all' 'peer'; do
    for level in 'summary_level' 'system_level'; do
      python -m sacrerouge.scripts.create_correlations_table \
        ${DIR}/output/tables/${metric}-${summarizer_type}-${level}.html \
        ${level} \
        --input ${DIR}/output/tac2008/correlations/${metric}-${summarizer_type}.json ModifiedPyramidScore TAC2008 \
        --input ${DIR}/output/tac2009/correlations/${metric}-${summarizer_type}.json ModifiedPyramidScore TAC2009 \
        --input ${DIR}/output/tac2010/correlations/${metric}-${summarizer_type}.json ModifiedPyramidScore TAC2010 \
        --input ${DIR}/output/tac2011/correlations/${metric}-${summarizer_type}.json ModifiedPyramidScore TAC2011
    done
  done
done