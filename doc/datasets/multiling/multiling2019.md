# MultiLing 2019
[Homepage](http://multiling.iit.demokritos.gr/pages/view/1644/multiling-2019)

For MultiLing 2019, we provide dataset readers for summary evaluation task:
```bash
sacrerouge setup-dataset multiling2019 \
    <output-dir>
```
Only the training annotations are provided on the MultiLing 2019 website, so we only parse those.
There were many summaries which were unjudged, and those are not included in our outputs.
The summaries do not have clear associations with summarization models, so we assign each summary a unique ID.

There were other tasks in 2019 (e.g., headline generation), but we do not include parsers for them. 

The output files are the following:
- `X/summaries.jsonl`: The judged summaries for language `X`
- `X/metrics.jsonl`: The corresponding scores for language `X`

## Citation
Please see the following citation for information about MultiLing 2019
```
@proceedings{ws-2019-multiling,
    title = "Proceedings of the Workshop MultiLing 2019: Summarization Across Languages, Genres and Sources",
    editor = "Giannakopoulos, George",
    month = sep,
    year = "2019",
    address = "Varna, Bulgaria",
    publisher = "INCOMA Ltd.",
    url = "https://aclanthology.org/W19-8900",
}
```