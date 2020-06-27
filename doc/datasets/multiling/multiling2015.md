# MultiLing 2015
[Homepage](http://multiling.iit.demokritos.gr/pages/view/1516/multiling-2015)

For MultiLing 2015, we provide dataset readers for the SDS task and the peer SDS summaries:
```bash
sacrerouge setup-dataset multiling2015 \
    <output-dir> \
    [--train-zip <path/to/TrainingData2015-20150314.zip>] \
    [--test-zip <path/to/SourceTextsV2b-20150214.zip>]
```
The last 2 arguments are downloadable from the MultiLing 2015 website (password required, so we cannot distribute it here).
They are required to setup the MDS dataset, otherwise only the SDS data will be setup.

The output files are the following:
- `sds/X.jsonl`: The data for the SDS summarization task for language `X`
- `sds/X.summaries.jsonl`: The peer submitted SDS summaries for language `X`
- `mds/X.jsonl`: The data for the MDS summarization task for language `X`

## Notes
The manual evaluations for the SDS task are not currently loaded because the library does not presently support loading pairwise metric comparisons (e.g., saying system A > B).
Additionally, I do not understand the judgment file format:
It has a column for each system name, then one for "quality" and "focus", but I do not know what they mean.

The SDS data has header information in an xml format which was not maintained in the json files.

The MDS test data does not contain the reference summaries.

## Citation
Please see the following citation for information about MultiLing 2015
```
@inproceedings{giannakopoulos2015multiling,
  title={Multiling 2015: multilingual summarization of single and multi-documents, on-line fora, and call-center conversations},
  author={Giannakopoulos, George and Kubina, Jeff and Conroy, John and Steinberger, Josef and Favre, Benoit and Kabadjov, Mijail and Kruschwitz, Udo and Poesio, Massimo},
  booktitle={Proceedings of the 16th Annual Meeting of the Special Interest Group on Discourse and Dialogue},
  pages={270--274},
  year={2015}
}
```