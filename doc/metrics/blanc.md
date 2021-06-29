# BLANC
BLANC [1] is a document-based evaluation metric.
It currently only supports single-document summaries.
Our implementation is a wrapper around the [original library](https://github.com/PrimerAI/blanc).
The name for this metric is `blanc`.

The scores replicate those calculated in [this](https://colab.research.google.com/drive/17pJ94L2kCL6QMBMflOm-H0ApBiOUWJ1H?usp=sharing) Colab notebook.

## Setting Up
Install the `blanc` pip package:
```
pip install blanc
```
The environment we used to successfully run the metric is located at `environments/blanc.yml`.

## Correlations
Here are the correlations of BLANC-Help to the annotations collected by Fabbri et al. (2020) on the CNN/DailyMail dataset.
They are very close to the correlations reported in the BLANC repository.
They are calculated using the default language model, bert-base-uncased.

Global correlations:
<table>
<tr>
<th>Summary Aspect</th>
<th>Spearman (Reported)</th>
<th>Spearman (Ours)</th>
<th>Kendall (Reported)</th>
<th>Kendall (Ours)</th>
</tr>
<tr>
<td>Coherence</td>
<td>0.122</td>
<td>0.122</td>
<td>0.09</td>
<td>0.09</td>
</tr>
<tr>
<td>Consistency</td>
<td>0.19</td>
<td>0.19</td>
<td>0.094</td>
<td>0.15</td>
</tr>
<tr>
<td>Fluency</td>
<td>0.089</td>
<td>0.089</td>
<td>0.051</td>
<td>0.069</td>
</tr>
<tr>
<td>Relevance</td>
<td>0.216</td>
<td>0.216</td>
<td>0.156</td>
<td>0.155</td>
</tr>
</table>

Summary-Level:
<table>
<tr>
<th>Summary Aspect</th>
<th>Spearman (Reported)</th>
<th>Spearman (Ours)</th>
<th>Kendall (Reported)</th>
<th>Kendall (Ours)</th>
</tr>
<tr>
<td>Consistency</td>
<td>0.738</td>
<td>0.738</td>
<td>0.567</td>
<td>0.567</td>
</tr>
</table>

## References
Oleg Vasilyev, Vedant Dharnidharka, John Bohannon. [Fill in the BLANC: Human-free quality estimation of document summaries](https://www.aclweb.org/anthology/2020.eval4nlp-1.2/). Eval4NLP, 2020.