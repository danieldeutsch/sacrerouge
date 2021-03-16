DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -e

wget https://github.com/mayhewsw/pytorch-truecaser/releases/download/v1.0/wiki-truecaser-model-en.tar.gz -O ${DIR}/wiki-truecaser-model-en.tar.gz
git clone https://github.com/mayhewsw/pytorch-truecaser ${DIR}/pytorch-truecaser