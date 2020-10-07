# QAEval
QAEval is a question-answering based metric for estimating the content quality of a summary [1].
It generates QA pairs from reference summaries, then uses a QA model to answer the questions against a candidate summary.
The final score is the portion of questions that were answered correctly.

## Setting Up
After installing SacreROUGE, then you must install the `qaeval` package:
```
pip install qaeval
```
The `qaeval` package uses PyTorch, Transformers, and AllenNLP.
In order to keep the required dependencies of SacreROUGE light, we chose to not incorporate the QAEval code into this repository.
Therefore, you must install the `qaeval` package or else the code will crash.

Then, QAEval uses pretrained question-generation and question-answering models, which must be downloaded:
```
sacrerouge setup-metric qa-eval
```
By default, this will download the model files to `~/.sacrerouge/metrics/qaeval/models`.
If you want to change this directoy, set the environment variable `SACREROUGE_DATA_ROOT` to whatever directory you want (instead of `~/.sacrerouge`).

To test your setup, run the following code:
```python
>>> import json
>>> from sacrerouge.metrics import QAEval
>>> 
>>> summary1 = 'Dan walked to the bakery this morning.'
>>> reference1 = 'Dan went to buy scones earlier this morning.'
>>> 
>>> # This line will load the generation and answer models into memory, so it may take some time to complete.
>>> qaeval = QAEval()
>>> 
>>> # To score an individual summary with a list of reference summaries. This example
>>> # only uses 1 reference, so it is wrapped in a list.
>>> scores = qaeval.score(summary1, [reference1])
>>> print(scores)
{'qa-eval': {'em': 0.5, 'f1': 0.5}}
>>>
>>> # To run batch scoring, use the score_all function and pass a list of summaries and
>>> # a list of list of references. Again, each instance here only has 1 reference, so it is wrapped
>>> # in a list
>>> summary2 = 'Roger Federer beat Rafael Nadal yesterday.'
>>> reference2 = 'Yesterday, Nadal lost to Federer'
>>> # scores_list is a list of size 2. scores_list[0] is the scores for summary1, and scores_list[1] for summary2
>>> scores_list = qaeval.score_all([summary1, summary2], [[reference1], [reference2]])
>>>
>>> # If you want the QA pairs used to score the summaries returned, add the return_qa_pairs=True argument
>>> # to any of the scoring methods. A tuple of size 2 will be returned. The first item is the scores
>>> # like above. The second item are the QA pairs.
>>> scores, qas = qaeval.score(summary2, [reference2], return_qa_pairs=True)
>>> 
>>> # qas[i][j] is the j-th QA pair for the i-th reference summary. The "probability" is the QA model's
>>> # probability for the prediction. "null_probability" is its probability there is no answer.
>>> print(json.dumps(qas[0][0], indent=2))
{
  "question": {
    "question_id": "915ed522cfe7b798bd23f299a6eca192",
    "question": "Who lost to Federer yesterday?",
    "answer": "Nadal",
    "sent_start": 0,
    "sent_end": 32,
    "answer_start": 11,
    "answer_end": 16
  },
  "prediction": {
    "prediction_id": "4a7d1ed414474e4033ac29ccb8653d9b",
    "prediction": "Rafael Nadal",
    "probability": 0.9939968367261187,
    "null_probability": 1.9474517469108735e-06,
    "em": 0,
    "f1": 0.6666666666666666
  }
}
>>>
>>> # If you pass the return_qa_pairs=True flag to score_all, it looks like this. "results" is parallel to "scores_list"
>>> # from before, but instead of only the scores, there is a tuple of the scores and the QA pairs 
>>> results = qaeval.score_all([summary1, summary2], [[reference1], [reference2]], return_qa_pairs=True)
>>> 
>>> scores1, qas1 = results[0]
>>> scores2, qas2 = results[1]
>>> print(json.dumps(qas1[0][0], indent=2))
{
  "question": {
    "question_id": "7cd86ecb09aa48c6e620b340f6a74592",
    "question": "Who went to buy scones earlier this morning?",
    "answer": "Dan",
    "sent_start": 0,
    "sent_end": 44,
    "answer_start": 0,
    "answer_end": 3
  },
  "prediction": {
    "prediction_id": "4a7d1ed414474e4033ac29ccb8653d9b",
    "prediction": "Dan",
    "probability": 0.9986048904063031,
    "null_probability": 2.303598142577244e-06,
    "em": 1,
    "f1": 1.0
  }
}
```


## Correlations
Here are the correlations of QAEval metrics to the "overall responsiveness" scores on the TAC datasets.
They differ slightly from those reported in the paper for reasons listed [here](https://github.com/danieldeutsch/qaeval).

Summary-level, peers only:
<table>
<tr>
<th></th>
<th colspan="3">TAC2008</th>
<th colspan="3">TAC2009</th>
<th colspan="3">TAC2010</th>
<th colspan="3">TAC2011</th>
</tr>
<tr>
<th></th>
<th>r</th>
<th>p</th>
<th>k</th>
<th>r</th>
<th>p</th>
<th>k</th>
<th>r</th>
<th>p</th>
<th>k</th>
<th>r</th>
<th>p</th>
<th>k</th>
</tr>
<tr>
<td>QA-EM</td>
<td>0.35</td>
<td>0.35</td>
<td>0.29</td>
<td>0.44</td>
<td>0.41</td>
<td>0.33</td>
<td>0.43</td>
<td>0.43</td>
<td>0.36</td>
<td>0.41</td>
<td>0.39</td>
<td>0.32</td>
</tr>
<tr>
<td>QA-F1</td>
<td>0.46</td>
<td>0.45</td>
<td>0.36</td>
<td>0.49</td>
<td>0.46</td>
<td>0.37</td>
<td>0.55</td>
<td>0.55</td>
<td>0.44</td>
<td>0.50</td>
<td>0.46</td>
<td>0.37</td>
</tr>
</table>

Summary-level, peers + references:
<table>
<tr>
<th></th>
<th colspan="3">TAC2008</th>
<th colspan="3">TAC2009</th>
<th colspan="3">TAC2010</th>
<th colspan="3">TAC2011</th>
</tr>
<tr>
<th></th>
<th>r</th>
<th>p</th>
<th>k</th>
<th>r</th>
<th>p</th>
<th>k</th>
<th>r</th>
<th>p</th>
<th>k</th>
<th>r</th>
<th>p</th>
<th>k</th>
</tr>
<tr>
<td>QA-EM</td>
<td>0.49</td>
<td>0.43</td>
<td>0.35</td>
<td>0.47</td>
<td>0.47</td>
<td>0.37</td>
<td>0.53</td>
<td>0.50</td>
<td>0.41</td>
<td>0.45</td>
<td>0.42</td>
<td>0.34</td>
</tr>
<tr>
<td>QA-F1</td>
<td>0.61</td>
<td>0.52</td>
<td>0.43</td>
<td>0.55</td>
<td>0.53</td>
<td>0.42</td>
<td>0.65</td>
<td>0.62</td>
<td>0.51</td>
<td>0.56</td>
<td>0.51</td>
<td>0.41</td>
</tr>
</table>

System-level, peers only:
<table>
<tr>
<th></th>
<th colspan="3">TAC2008</th>
<th colspan="3">TAC2009</th>
<th colspan="3">TAC2010</th>
<th colspan="3">TAC2011</th>
</tr>
<tr>
<th></th>
<th>r</th>
<th>p</th>
<th>k</th>
<th>r</th>
<th>p</th>
<th>k</th>
<th>r</th>
<th>p</th>
<th>k</th>
<th>r</th>
<th>p</th>
<th>k</th>
</tr>
<tr>
<td>QA-EM</td>
<td>0.92</td>
<td>0.89</td>
<td>0.74</td>
<td>0.71</td>
<td>0.88</td>
<td>0.71</td>
<td>0.91</td>
<td>0.88</td>
<td>0.72</td>
<td>0.90</td>
<td>0.78</td>
<td>0.59</td>
</tr>
<tr>
<td>QA-F1</td>
<td>0.90</td>
<td>0.86</td>
<td>0.68</td>
<td>0.78</td>
<td>0.88</td>
<td>0.72</td>
<td>0.93</td>
<td>0.88</td>
<td>0.75</td>
<td>0.94</td>
<td>0.82</td>
<td>0.64</td>
</tr>
</table>

System-level, peers + references:
<table>
<tr>
<th></th>
<th colspan="3">TAC2008</th>
<th colspan="3">TAC2009</th>
<th colspan="3">TAC2010</th>
<th colspan="3">TAC2011</th>
</tr>
<tr>
<th></th>
<th>r</th>
<th>p</th>
<th>k</th>
<th>r</th>
<th>p</th>
<th>k</th>
<th>r</th>
<th>p</th>
<th>k</th>
<th>r</th>
<th>p</th>
<th>k</th>
</tr>
<tr>
<td>QA-EM</td>
<td>0.97</td>
<td>0.92</td>
<td>0.79</td>
<td>0.68</td>
<td>0.92</td>
<td>0.77</td>
<td>0.96</td>
<td>0.93</td>
<td>0.79</td>
<td>0.81</td>
<td>0.81</td>
<td>0.63</td>
</tr>
<tr>
<td>QA-F1</td>
<td>0.96</td>
<td>0.90</td>
<td>0.74</td>
<td>0.78</td>
<td>0.92</td>
<td>0.77</td>
<td>0.97</td>
<td>0.93</td>
<td>0.81</td>
<td>0.89</td>
<td>0.88</td>
<td>0.72</td>
</tr>
</table>

## Citation
If you use this metric, please cite the following work
```
@misc{deutsch2020questionanswering,
      title={{Towards Question-Answering as an Automatic Metric for Evaluating the Content Quality of a Summary}}, 
      author={Daniel Deutsch and Tania Bedrax-Weiss and Dan Roth},
      year={2020},
      eprint={2010.00490},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```

## References
[1] Daniel Deutsch, Tania Bedrax-Weiss, and Dan Roth. [Towards Question-Answering as an Automatic Metric for Evaluating the Content Quality of a Summary](https://arxiv.org/abs/2010.00490). 2020.
