# BERTScore
BERTScore [1] is a reference-based evaluation metric based on calculating the similarity of two summaries' BERT embeddings.
Our implementation calls the `score` function from [our fork](https://github.com/danieldeutsch/bert_score) of the [original repository](https://github.com/Tiiiger/bert_score), which we modified to expose creating the IDF dictionaries.

## Setting Up
BERTScore can be installed via pip:
```bash
pip install git+https://github.com/danieldeutsch/bert_score
```
This must reference our fork of the code that has the IDF calculation exposed.
After that, the metric can be used within SacreROUGE.

## References
[1] Tianyi Zhang, Varsha Kishore, Felix Wu, Kilian Q.Weinberger, and Yoav Artzi. [BERTScore: Evaluating Text Generation with BERT](https://arxiv.org/abs/1904.09675). ICLR 2020.