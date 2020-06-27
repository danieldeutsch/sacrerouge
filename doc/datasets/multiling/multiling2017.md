# MultiLing 2017
[Homepage](http://multiling.iit.demokritos.gr/pages/view/1616/multiling-2017)

For MultiLing 2017, we provide dataset readers for the SDS task and the peer SDS summaries:
```bash
sacrerouge setup-dataset multiling2017 \
    <output-dir>
```

The output files are the following:
- `sds/X.jsonl`: The data for the SDS summarization task for language `X`
- `sds/X.summaries.jsonl`: The peer submitted SDS summaries for language `X`

## Notes
The manual/automatic evaluations for the SDS task are not currently loaded because the library does not presently support loading pairwise metric comparisons (e.g., saying system A > B).

The SDS data has header information in an xml format which was not maintained in the json files.

## Citation
Please see the following citation for information about MultiLing 2017
```
@inproceedings{giannakopoulos2017multiling,
  title={Multiling 2017 overview},
  author={Giannakopoulos, George and Conroy, John and Kubina, Jeff and Rankel, Peter A and Lloret, Elena and Steinberger, Josef and Litvak, Marina and Favre, Benoit},
  booktitle={Proceedings of the MultiLing 2017 workshop on summarization and summary evaluation across source types and genres},
  pages={1--6},
  year={2017}
}
```