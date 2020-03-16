if [ "$#" -ne 1 ]; then
    echo "Usage: sh datasets/duc-tac/tac2010/setup.sh <path/to/duc-tac-data>"
    exit
fi

root=$1

version="v1.0"

python -m sacrerouge.datasets.duc_tac.tac2010.task1 \
  ${root}/from-nist/TAC2010_Summarization_Documents.tgz \
  ${root}/scrapes/tac.nist.gov/protected/past-aquaint-aquaint2/2010/GuidedSumm2010_eval.tgz \
  ${root}/scrapes/tac.nist.gov/protected/past-aquaint-aquaint2/2010/GuidedSumm10_test_topics.xml.txt \
  datasets/duc-tac/tac2010/${version}

python -m sacrerouge.datasets.duc_tac.tac2010.metrics \
  ${root}/scrapes/tac.nist.gov/protected/past-aquaint-aquaint2/2010/GuidedSumm2010_eval.tgz \
  ${root}/scrapes/tac.nist.gov/protected/past-aquaint-aquaint2/2010/AESOP2010_eval.tgz \
  datasets/duc-tac/tac2010/${version}
