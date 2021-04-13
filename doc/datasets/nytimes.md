# New York Times
The New York Times dataset [1] is a collection of New York Times articles along with abstract summaries.
Our setup script parses the articles, headlines, abstracts, and publication dates.
The train/valid/test split follows those defined [here](https://github.com/jiacheng-xu/DiscoBERT/tree/release/data_preparation/urls_nyt).

The setup command can be run as follows:
```
sacrerouge setup-dataset nytimes <LDC2008T19-tar> <output-dir>
```
The `LDC2008T19-tar` argument should be the `nyt_corpus_LDC2008T19.tgz` provided in [LDC2008T19](https://catalog.ldc.upenn.edu/LDC2008T19), which you can access via the LDC.

The output will have `train.jsonl.gz`, `valid.jsonl.gz`, and `test.jsonl.gz` files.
Each line will have the following format:
```json
{
  "instance_id": "1234",
  "document": {
    "date": "2007-01-01",
    "headline": "The article's headline",
    "text": [
      "The text of paragraph 1",
      "The text of paragraph 2"
    ]
  },
  "summary": {
    "text": "The abstract text"
  }
}
```

## Notes
The headline comes from the xml node `body/body.head/hedline/hl1` if it exists, otherwise `body/body.head/hedline/hl2`.
The body comes from `p` nodes under `body/body.head/abstract`.
The summary comes from the xml node `body/body.content/block[@class="full_text"]/p`.
Each item in the document to a `p` node.
No sentence breaking was run, so each `p` node could have multiple sentences.
The abstract has multiple sentences which are often separated with a semi-colon.

There are 137,778 training 17,222 validation, and 17,223 testing instances.

## References
[1] The New York Times Annotated Corpus. https://catalog.ldc.upenn.edu/LDC2008T19