if [ "$#" -ne 1 ]; then
    echo "Usage: sh datasets/duc-tac/tac2009/setup.sh <path/to/duc-tac-data>"
    exit
fi

root=$1

version="v1.0"

python -m sacrerouge.datasets.duc_tac.tac2009.task1 \
  ${root}/from-nist/TAC2009_Summarization_Documents.tgz \
  ${root}/scrapes/tac.nist.gov/protected/past-aquaint2/2009/UpdateSumm09_eval.tar.gz \
  ${root}/scrapes/tac.nist.gov/protected/past-aquaint2/2009/UpdateSumm09_test_topics.xml.txt \
  datasets/duc-tac/tac2009/${version}

python -m sacrerouge.datasets.duc_tac.tac2009.metrics \
  ${root}/scrapes/tac.nist.gov/protected/past-aquaint2/2009/UpdateSumm09_eval.tar.gz \
  ${root}/scrapes/tac.nist.gov/protected/past-aquaint2/2009/AESOP09_eval.tar.gz \
  datasets/duc-tac/tac2009/${version}
