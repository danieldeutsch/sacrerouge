# Fabbri 2020
This dataset contains expert and Turker annotations for summaries on the CNN/DailyMail dataset as collected in [1].
The setup command will save the summaries and references for all of the systems and their corresponding annotations.
See this [Github repository](https://github.com/Yale-LILY/SummEval) for more details.

```bash
sacrerouge setup-dataset fabbri2020 <output-dir>
```

The output files are the following:
- `summaries.jsonl`: The model output summaries and the ground-truth references
- `summaries-with-crowd.jsonl`: The model output summaries and the ground-truth and ten crowdsourced references
- `metrics.jsonl`: The expert and Turker annotations that correspond to `summaries.jsonl` and `summaries-with-crowd.jsonl`

## References
[1] Fabbri, Alexander R and Kryscinski, Wojciech and McCann, Bryan and Xiong, Caiming and Socher, Richard and Radev, Dragomir. "[SummEval: Re-evaluating Summarization Evaluation](https://arxiv.org/pdf/2007.12626.pdf)". 2020