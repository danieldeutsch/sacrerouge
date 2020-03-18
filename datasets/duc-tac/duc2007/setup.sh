if [ "$#" -ne 1 ]; then
    echo "Usage: sh datasets/duc-tac/duc2007/setup.sh <path/to/duc-tac-data>"
    exit
fi

root=$1

version="v1.0"

python -m sacrerouge.datasets.duc_tac.duc2007.tasks \
  ${root}/from-nist/DUC2007_Summarization_Documents.tgz \
  ${root}/scrapes/duc.nist.gov/past_duc_aquaint/duc2007/results/mainEval.tar.gz \
  ${root}/scrapes/duc.nist.gov/past_duc_aquaint/duc2007/results/updateEval.tar.gz \
  ${root}/scrapes/duc.nist.gov/past_duc_aquaint/duc2007/testdata/duc2007_topics.sgml \
  ${root}/scrapes/duc.nist.gov/past_duc_aquaint/duc2007/testdata/duc2007_UPDATEtopics.sgml \
  datasets/duc-tac/duc2007/${version}

python -m sacrerouge.datasets.duc_tac.duc2007.metrics \
  ${root}/scrapes/duc.nist.gov/past_duc_aquaint/duc2007/results/mainEval.tar.gz \
  ${root}/scrapes/duc.nist.gov/past_duc_aquaint/duc2007/results/updateEval.tar.gz \
  datasets/duc-tac/duc2007/${version}
