# Fabbri 2020
This dataset contains expert and Turker annotations for summaries on the CNN/DailyMail dataset as collected in [1].
The setup command will save the summaries and references for all of the systems and their corresponding annotations and input documents.
See this [Github repository](https://github.com/Yale-LILY/SummEval) for more details.

```bash
sacrerouge setup-dataset fabbri2020 <cnn-tar-path> <dailymail-tar-path> <output-dir>
```
The `<cnn-tar-path>` and `<dailymail-tar-path>` are paths to the downloaded "story" tarfiles from [here](https://cs.nyu.edu/~kcho/DMQA/). 

The output files are the following:
- `summaries.jsonl`: The model output summaries with their input documents and the ground-truth references
- `summaries-with-crowd.jsonl`: The model output summaries with their input documents and the ground-truth and ten crowdsourced references
- `metrics.jsonl`: The expert and Turker annotations that correspond to `summaries.jsonl` and `summaries-with-crowd.jsonl`

Notes:
- The raw data does not identify which reference summary is the original ground-truth reference, but after checking a handful of instances, it appears as if it is always the first reference in the list of references.
That first reference is the one included in `summaries.jsonl`. ([Confirmed](https://github.com/Yale-LILY/SummEval/issues/8))
- To make the crowd summaries distinct, each is given a `summarizer_id` of `turker-` followed by a number from 1 to 10.
It is not necessarily the case that the summaries identified by `turker-i` were all written by the same person and should not be treated as such.
- There are many (input document, summary) pairs that were not judged and not processed by this script.
We need to figure out exactly what to do with them.
Several models have multiple output files (M5 has "outputs_rouge.aligned.jsonl" and "outputs_rouge+coh.aligned.jsonl")
but the "summaries.jsonl" will only have one of those summaries (e.g. in "summaries.jsonl" there is only one summary for "M5").
We need to have some way to distinguish the different outputs to put all of the aligned document + summary pairs into one file.

## Correlations
Here are the correlations of some of the metrics implemented in this library to the responsiveness scores in this dataset.

Single-reference, summary-level
<table>
<tr>
<th></th>
<th colspan="3">Fabbri2020</th>
</tr>
<tr>
<th></th>
<th>r</th>
<th>p</th>
<th>k</th>
</tr>
<tr>
<td>R1-P</td>
<td>0.13</td>
<td>0.12</td>
<td>0.09</td>
</tr>
<tr>
<td>R1-R</td>
<td>0.31</td>
<td>0.28</td>
<td>0.23</td>
</tr>
<tr>
<td>R1-F1</td>
<td>0.28</td>
<td>0.26</td>
<td>0.20</td>
</tr>
<tr>
<td>R2-P</td>
<td>0.15</td>
<td>0.13</td>
<td>0.09</td>
</tr>
<tr>
<td>R2-R</td>
<td>0.26</td>
<td>0.23</td>
<td>0.18</td>
</tr>
<tr>
<td>R2-F1</td>
<td>0.23</td>
<td>0.19</td>
<td>0.14</td>
</tr>
<tr>
<td>BERTScore-P</td>
<td>0.17</td>
<td>0.17</td>
<td>0.13</td>
</tr>
<tr>
<td>BERTScore-R</td>
<td>0.37</td>
<td>0.35</td>
<td>0.27</td>
</tr>
<tr>
<td>BERTScore-F1</td>
<td>0.29</td>
<td>0.28</td>
<td>0.22</td>
</tr>
<tr>
<td>MoverScore</td>
<td>0.28</td>
<td>0.24</td>
<td>0.18</td>
</tr>
<tr>
<td>QAEval-EM</td>
<td>0.23</td>
<td>0.23</td>
<td>0.19</td>
</tr>
<tr>
<td>QAEval-F1</td>
<td>0.30</td>
<td>0.29</td>
<td>0.22</td>
</tr>
</table>

Single-reference, system-level
<table>
<tr>
<th></th>
<th colspan="3">Fabbri2020</th>
</tr>
<tr>
<th></th>
<th>r</th>
<th>p</th>
<th>k</th>
</tr>
<tr>
<td>R1-P</td>
<td>0.29</td>
<td>0.15</td>
<td>0.03</td>
</tr>
<tr>
<td>R1-R</td>
<td>0.55</td>
<td>0.56</td>
<td>0.42</td>
</tr>
<tr>
<td>R1-F1</td>
<td>0.61</td>
<td>0.62</td>
<td>0.50</td>
</tr>
<tr>
<td>R2-P</td>
<td>0.49</td>
<td>0.41</td>
<td>0.25</td>
</tr>
<tr>
<td>R2-R</td>
<td>0.65</td>
<td>0.78</td>
<td>0.57</td>
</tr>
<tr>
<td>R2-F1</td>
<td>0.64</td>
<td>0.60</td>
<td>0.43</td>
</tr>
<tr>
<td>BERTScore-P</td>
<td>0.18</td>
<td>0.11</td>
<td>0.02</td>
</tr>
<tr>
<td>BERTScore-R</td>
<td>0.84</td>
<td>0.91</td>
<td>0.75</td>
</tr>
<tr>
<td>BERTScore-F1</td>
<td>0.54</td>
<td>0.40</td>
<td>0.28</td>
</tr>
<tr>
<td>MoverScore</td>
<td>0.56</td>
<td>0.54</td>
<td>0.42</td>
</tr>
<tr>
<td>QAEval-EM</td>
<td>0.80</td>
<td>0.91</td>
<td>0.77</td>
</tr>
<tr>
<td>QAEval-F1</td>
<td>0.82</td>
<td>0.91</td>
<td>0.77</td>
</tr>
</table>

Multi-reference, summary-level
<table>
<tr>
<th></th>
<th colspan="3">Fabbri2020</th>
</tr>
<tr>
<th></th>
<th>r</th>
<th>p</th>
<th>k</th>
</tr>
<tr>
<td>R1-P</td>
<td>0.13</td>
<td>0.14</td>
<td>0.10</td>
</tr>
<tr>
<td>R1-R</td>
<td>0.33</td>
<td>0.29</td>
<td>0.23</td>
</tr>
<tr>
<td>R1-F1</td>
<td>0.36</td>
<td>0.33</td>
<td>0.25</td>
</tr>
<tr>
<td>R2-P</td>
<td>0.20</td>
<td>0.21</td>
<td>0.16</td>
</tr>
<tr>
<td>R2-R</td>
<td>0.34</td>
<td>0.31</td>
<td>0.24</td>
</tr>
<tr>
<td>R2-F1</td>
<td>0.33</td>
<td>0.29</td>
<td>0.22</td>
</tr>
<tr>
<td>BERTScore-P</td>
<td>0.18</td>
<td>0.19</td>
<td>0.14</td>
</tr>
<tr>
<td>BERTScore-R</td>
<td>0.42</td>
<td>0.38</td>
<td>0.29</td>
</tr>
<tr>
<td>BERTScore-F1</td>
<td>0.31</td>
<td>0.31</td>
<td>0.24</td>
</tr>
<tr>
<td>MoverScore</td>
<td>0.33</td>
<td>0.27</td>
<td>0.21</td>
</tr>
<tr>
<td>QAEval-EM</td>
<td>0.33</td>
<td>0.29</td>
<td>0.22</td>
</tr>
<tr>
<td>QAEval-F1</td>
<td>0.40</td>
<td>0.35</td>
<td>0.27</td>
</tr>
</table>

Multi-reference, system-level
<table>
<tr>
<th></th>
<th colspan="3">Fabbri2020</th>
</tr>
<tr>
<th></th>
<th>r</th>
<th>p</th>
<th>k</th>
</tr>
<tr>
<td>R1-P</td>
<td>0.03</td>
<td>0.08</td>
<td>0.02</td>
</tr>
<tr>
<td>R1-R</td>
<td>0.38</td>
<td>0.30</td>
<td>0.23</td>
</tr>
<tr>
<td>R1-F1</td>
<td>0.55</td>
<td>0.77</td>
<td>0.58</td>
</tr>
<tr>
<td>R2-P</td>
<td>0.34</td>
<td>0.26</td>
<td>0.13</td>
</tr>
<tr>
<td>R2-R</td>
<td>0.41</td>
<td>0.29</td>
<td>0.23</td>
</tr>
<tr>
<td>R2-F1</td>
<td>0.57</td>
<td>0.64</td>
<td>0.43</td>
</tr>
<tr>
<td>BERTScore-P</td>
<td>0.13</td>
<td>0.14</td>
<td>0.05</td>
</tr>
<tr>
<td>BERTScore-R</td>
<td>0.80</td>
<td>0.85</td>
<td>0.70</td>
</tr>
<tr>
<td>BERTScore-F1</td>
<td>0.41</td>
<td>0.48</td>
<td>0.38</td>
</tr>
<tr>
<td>MoverScore</td>
<td>0.46</td>
<td>0.36</td>
<td>0.30</td>
</tr>
<tr>
<td>QAEval-EM</td>
<td>0.60</td>
<td>0.58</td>
<td>0.43</td>
</tr>
<tr>
<td>QAEval-F1</td>
<td>0.62</td>
<td>0.65</td>
<td>0.48</td>
</tr>
</table>

## References
[1] Fabbri, Alexander R and Kryscinski, Wojciech and McCann, Bryan and Xiong, Caiming and Socher, Richard and Radev, Dragomir. "[SummEval: Re-evaluating Summarization Evaluation](https://arxiv.org/pdf/2007.12626.pdf)". 2020