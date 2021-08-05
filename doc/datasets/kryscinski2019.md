# Kryściński 2019
This dataset contains the factuality annotations collected in [Evaluating the Factual Consistency of Abstractive Text Summarization](https://arxiv.org/abs/1910.12840).

To setup the dataset, run
```shell script
sacrerouge setup-dataset kryscinski2019 <output-dir>
``` 

The output directory will contain `valid.jsonl` and `test.jsonl` files.
Each JSON item will contain:
- The instance ID
- A dummy summarizer name
- The text of the CNN/DailyMail document
- The claim that was evaluated, which we store in the "summary" field
- The label of the instance, either "CORRECT" or "INCORRECT"