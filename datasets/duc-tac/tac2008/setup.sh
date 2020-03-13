if [ "$#" -ne 1 ]; then
    echo "Usage: sh datasets/duc-tac/tac2008/setup.sh <path/to/duc-tac-data>"
    exit
fi

root=$1

version="v1.0"

python -m sacrerouge.datasets.duc_tac.tac2008.task1 \
  ${root}/from-nist/TAC2008_Summarization_Documents.tgz \
  ${root}/scrapes/tac.nist.gov/protected/past-aquaint2/2008/UpdateSumm08_eval.tar.gz \
  ${root}/scrapes/tac.nist.gov/protected/past-aquaint2/2008/UpdateSumm08_test_topics.xml.txt \
  datasets/duc-tac/tac2008/${version}

python -m sacrerouge.datasets.duc_tac.tac2008.judgments \
  ${root}/scrapes/tac.nist.gov/protected/past-aquaint2/2008/UpdateSumm08_eval.tar.gz \
  datasets/duc-tac/tac2008/${version}
