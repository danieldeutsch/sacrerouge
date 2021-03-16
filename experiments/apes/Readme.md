## Truecaser information
Upon running the APES metric on the Fabbri et al., (2020) dataset, we found that the named entity tagger had difficulty finding candidate entities in the lowercased candidate summaries.
That cannot be fixed properly because some of the models from the dataset output uncased summaries.
To try and address that, we run a truecaser on the summaries before evaluating them.

The truecaser we use is from [here](https://github.com/mayhewsw/pytorch-truecaser).
We successfully created a conda environment for this by installing the packages in that repo, followed by `pip install scikit-learn==0.22.2` (I believe this was fixed in a newer version, so potentially unnecessary).

Then, run the `setup-fabbri2020.sh` script from the root of the repository to download the truecaser code and model before running `run-fabbri2020.sh`.