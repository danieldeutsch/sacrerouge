if [ "$#" -ne 1 ]; then
    echo "Usage: sh datasets/duc-tac/duc2005/setup.sh <path/to/duc-tac-data>"
    exit
fi

root=$1

version="v1.0"

python -m sacrerouge.datasets.duc_tac.duc2005.task1 \
  ${root}/from-nist/DUC2005_Summarization_Documents.tgz \
  ${root}/scrapes/duc.nist.gov/past_duc/duc2005/results/NIST/results.tar \
  ${root}/scrapes/duc.nist.gov/past_duc/duc2005/testdata/duc2005_topics.sgml \
  datasets/duc-tac/duc2005/${version}

python -m sacrerouge.datasets.duc_tac.duc2005.metrics \
  ${root}/scrapes/duc.nist.gov/past_duc/duc2005/results/NIST/results.tar \
  datasets/duc-tac/duc2005/${version}
