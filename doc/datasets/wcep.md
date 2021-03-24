# WCEP
The Wikipedia Current Events Portal dataset is a multi-document summarzation dataset collected by [1].
To parse the dataset, run
```
sacrerouge setup-dataset wcep <output-dir>
```
Each document has an `origin` field that indicates if it came from WCEP or CommonCrawl.

We noticed there are many source documents that are duplicates within the same cluster.
Our processing has removed those and gave priority to the ones from WCEP over CommonCrawl.
The total number of duplicate source documents removed is 48912 from train, 6978 from valid, and 6183 from test.

Further, 981 documents in train, 249 in valid, and 145 in test were empty.
They were removed.

## References
[1] Demian Gholipour Ghalandari, Chris Hokamp, Nghia The Pham, John Glover, and Georgiana Ifrim. [A Large-Scale Multi-Document Summarization Dataset from the Wikipedia Current Events Portal](https://arxiv.org/pdf/2005.10070.pdf). ACL 2020.