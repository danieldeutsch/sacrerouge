# BLANC
BLANC [1] is a document-based evaluation metric.
It currently only supports single-document summaries.
Our implementation is a wrapper around the [original library](https://github.com/PrimerAI/blanc).
The name for this metric is `blanc`.

## Setting Up
Install the `blanc` pip package:
```
pip install blanc
```
Then we manually installed `transformers==2.5.1` based on the instructions on the Github repo.
The default transformers version which was installed did not work.

Currently, the unit tests do not produce the scores reported in the official Github repository, but I think it might be related to the random seed which is not set in the constructor of the class but in their main function.

## Correlations
Here are the correlations of BLANC to the judgments they provided in their paper (see [here](../datasets/vasilyev2020.md)).
Since there is no identification of which summary was produced by which system in the dataset, these correlations are the global correlations.
The correlations appear to reproduce the BLANC-Help with gap = 6 that they reported in their paper, around 0.34.  

CNN-DailyMail:
<table>
<tr>
<th></th>
<th colspan="3">cnn-dailymail</th>
</tr>
<tr>
<th></th>
<th>r</th>
<th>p</th>
<th>k</th>
</tr>
<tr>
<td>BLANC-Help-Gap-2</td>
<td>0.36</td>
<td>0.38</td>
<td>0.27</td>
</tr>
<tr>
<td>BLANC-Help-Gap-6</td>
<td>0.33</td>
<td>0.34</td>
<td>0.24</td>
</tr>
<tr>
<td>BLANC-Tune-Gap-2</td>
<td>0.36</td>
<td>0.38</td>
<td>0.27</td>
</tr>
<tr>
<td>BLANC-Tune-Gap-6</td>
<td>0.33</td>
<td>0.34</td>
<td>0.24</td>
</tr>
</table>

DailyNews:
<table>
<tr>
<th></th>
<th colspan="3">dailynews</th>
</tr>
<tr>
<th></th>
<th>r</th>
<th>p</th>
<th>k</th>
</tr>
<tr>
<td>BLANC-Help-Gap-2</td>
<td>0.38</td>
<td>0.35</td>
<td>0.25</td>
</tr>
<tr>
<td>BLANC-Help-Gap-6</td>
<td>0.35</td>
<td>0.32</td>
<td>0.23</td>
</tr>
<tr>
<td>BLANC-Tune-Gap-2</td>
<td>0.38</td>
<td>0.35</td>
<td>0.25</td>
</tr>
<tr>
<td>BLANC-Tune-Gap-6</td>
<td>0.35</td>
<td>0.32</td>
<td>0.23</td>
</tr>
</table>

## References
Oleg Vasilyev, Vedant Dharnidharka, John Bohannon. [Fill in the BLANC: Human-free quality estimation of document summaries](https://www.aclweb.org/anthology/2020.eval4nlp-1.2/). Eval4NLP, 2020.