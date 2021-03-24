# Multi-News
The Multi-News dataset is a collection of multi-document news summarization instances collected in [1].
Our code downloads and parses the dataset into a SacreROUGE format.

To set up the dataset, run:
```
sacrerouge setup-dataset multinews <output-dir>
```

It will output the following files:
    - `{train,valid,test}.jsonl.gz`: The data splits with `instance_id`, `documents`, and `summary` fields.
    Instances with 0 source documents are removed (see below).
    - `{train,valid,test}.multi.jsonl.gz`: The above files but with only the instances which are multi-document.
    See [here](https://github.com/Alex-Fabbri/Multi-News/issues/11) for more details about why there are some single-document summaries.
 
## Notes
The data comes from this repository: https://github.com/Alex-Fabbri/Multi-News.
The documents come from the ["raw data, bad retrievals removed"](https://drive.google.com/drive/folders/1jwBzXBVv8sfnFrlzPnSUBHEEAbpIUnFq) folder.
The summaries come from the ["raw data"](https://drive.google.com/open?id=1uDarzpu2HFc-vjXNJCRv2NIHzakpSGOw) folder.
Both are linked in the Readme at the root of the repo.

Each instance has an ID, which we take from [here](https://github.com/Alex-Fabbri/Multi-News/tree/master/data/ids).
Since we did not collect the data ourselves and the documents and summaries files don't have the IDs, we don't know for certain that the IDs are aligned with the documents and summaries files.
We assume that they are.

The expected number of instances with a given number of source documents is given [here](https://github.com/Alex-Fabbri/Multi-News/issues/11).
Our counts differ slightly from this.
After splitting on `|||||`, the numbers are:
```
Train Counter({2: 23741, 3: 12577, 4: 4921, 5: 1846, 6: 706, 1: 498, 7: 371, 8: 194, 9: 81, 10: 29, 0: 8}), total = 44972
Valid Counter({2: 3066, 3: 1555, 4: 610, 5: 195, 6: 79, 1: 58, 7: 38, 8: 13, 9: 7, 0: 1}), total = 5622
Test Counter({2: 3022, 3: 1540, 4: 609, 5: 219, 6: 96, 1: 71, 7: 40, 8: 15, 9: 8, 10: 1, 0: 1}), total = 5622
```

After filtering empty documents (documents with all empty lines), the numbers are:
```
Train Counter({2: 23741, 3: 12577, 4: 4921, 5: 1846, 6: 706, 1: 498, 7: 371, 8: 194, 9: 81, 10: 29}), total = 44964
Valid Counter({2: 3066, 3: 1555, 4: 610, 5: 195, 6: 79, 1: 58, 7: 38, 8: 13, 9: 7}), total = 5621
Test Counter({2: 3022, 3: 1540, 4: 609, 5: 219, 6: 96, 1: 71, 7: 40, 8: 15, 9: 8, 10: 1}) , total = 5621
```
We found 14 individual empty documents.
Our output files remove the instances with 0 source documents.
If you use this dataset to publish, it is probably worth investigating why these instances have 0 documents and verify that they also have 0 documents in the preprocessed code released in the original repository.

## References
[1] Alexander Fabbri, Irene Li, Tianwei She, Suyi Li, and Dragomir Radev. [Multi-News: a Large-Scale Multi-Document Summarization Dataset and Abstractive Hierarchical Model](https://arxiv.org/pdf/1906.01749.pdf). ACL 2019.