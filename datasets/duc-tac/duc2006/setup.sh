if [ "$#" -ne 1 ]; then
    echo "Usage: sh datasets/duc-tac/duc2006/setup.sh <path/to/duc-tac-data>"
    exit
fi

root=$1

version="v1.0"

python -m sacrerouge.datasets.duc_tac.duc2006.task1 \
  ${root}/from-nist/DUC2006_Summarization_Documents.tgz \
  ${root}/scrapes/duc.nist.gov/past_duc_aquaint/duc2006/results/NIST/NISTeval.tar.gz \
  ${root}/scrapes/duc.nist.gov/past_duc_aquaint/duc2006/testdata/duc2006_topics.sgml \
  datasets/duc-tac/duc2006/${version}
