# MultiLing 2013
[Homepage](http://multiling.iit.demokritos.gr/pages/view/662/multiling-2013)

For MultiLing 2013, we provide dataset readers for the SDS task, MDS task, and MDS evaluation:
```bash
sacrerouge setup-dataset multiling2013 \
    <output-dir> \
    [--mds-documents-zip <path/to/SourceTextsV2b.zip>] \
    [--mds-model-summaries-zip <path/to/ModelSummaries- 20130605.zip>] \
    [--mds-peer-summaries-zip <path/to/PeerSummaries - 20130601.zip>] \
    [--metrics-zip <path/to/MultiDocument-ManualGrades-20130717.zip>]
```
The last 4 arguments are downloadable from the MultiLing 2013 website (password required, so we cannot distribute it here).
They are required to setup the MDS dataset, otherwise only the SDS data will be setup.

The output files are the following:
- `sds/X.jsonl`: The data for the SDS summarization task for language `X`
- `mds/X.jsonl`: The data for the MDS summarization task for language `X`
- `mds/X.summaries.jsonl`: The model and peer MDS summaries for language `X`
- `mds/X.metrics.jsonl`: The evaluation metrics for the model an peer MDS summaries for language `X` (does not exist for all languages) 

## Notes
The ROUGE and n-gram graph scores (AutoSummEng, etc.) were provided in the evaluation data but were not loaded here.

The SDS data has header information in an xml format which was not maintained in the json files.

## Citation
Please see the following citation for information about MultiLing 2013
```
@inproceedings{giannakopoulos2013multi,
  title={Multi-document multilingual summarization and evaluation tracks in ACL 2013 multiling workshop},
  author={Giannakopoulos, George},
  booktitle={Proceedings of the MultiLing 2013 workshop on multilingual multi-document summarization},
  pages={20--28},
  year={2013}
}
```