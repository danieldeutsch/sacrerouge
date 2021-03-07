# SUPERT
SUPERT is a document-based reference-free content quality evaluation metric proposed by [1].

## Setting Up
The implementation in SacreROUGE is using [our fork](https://github.com/danieldeutsch/SUPERT) of the [original repository](https://github.com/yg211/acl20-ref-free-eval).
Our fork adds functionality to run the metric on a collection of (summary, documents) pairs instead of one instance at a time.

Because the code has large dependencies, you need to create a conda environment to run SUPERT.
We used [this environment file](../../environments/supert.yml) which was based on the requirements from the original repository.
The name of the conda environment must be passed to the `SUPERT` constructor.

After the conda environment is created, run this command to download the code:
```
sacrerouge setup-metric supert
```

To verify your installation, set the environment variable `SUPERT_ENV` to be the name of the conda environment, then run:
```
pytest sacrerouge/tests/metrics/supert_test.py
```

## Correlations
Here are the correlations of SUPERT to the "overall responsiveness" human judgments on several datasets.

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
<td>SUPERT</td>
<td>0.44</td>
<td>0.42</td>
<td>0.34</td>
<td>0.46</td>
<td>0.42</td>
<td>0.33</td>
<td>0.55</td>
<td>0.58</td>
<td>0.47</td>
<td>0.51</td>
<td>0.48</td>
<td>0.39</td>
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
<td>SUPERT</td>
<td>0.24</td>
<td>0.29</td>
<td>0.23</td>
<td>0.26</td>
<td>0.29</td>
<td>0.22</td>
<td>0.45</td>
<td>0.46</td>
<td>0.36</td>
<td>0.42</td>
<td>0.36</td>
<td>0.28</td>
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
<td>SUPERT</td>
<td>0.90</td>
<td>0.88</td>
<td>0.70</td>
<td>0.74</td>
<td>0.79</td>
<td>0.63</td>
<td>0.85</td>
<td>0.89</td>
<td>0.76</td>
<td>0.85</td>
<td>0.83</td>
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
<td>SUPERT</td>
<td>0.07</td>
<td>0.45</td>
<td>0.40</td>
<td>0.11</td>
<td>0.41</td>
<td>0.35</td>
<td>0.47</td>
<td>0.60</td>
<td>0.47</td>
<td>0.44</td>
<td>0.49</td>
<td>0.38</td>
</tr>
</table>

Here are the correlations to the annotations provided by Bhandari et al., (2020).
Summary-level:
<table>
<tr>
<th></th>
<th colspan="3">Bhandari2020-Abs</th>
<th colspan="3">Bhandari2020-Ext</th>
<th colspan="3">Bhandari2020-Mix</th>
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
</tr>
<tr>
<td>SUPERT</td>
<td>0.12</td>
<td>0.23</td>
<td>0.18</td>
<td>0.14</td>
<td>0.12</td>
<td>0.11</td>
<td>0.18</td>
<td>0.24</td>
<td>0.19</td>
</tr>
</table>

System-level:
<table>
<tr>
<th></th>
<th colspan="3">Bhandari2020-Abs</th>
<th colspan="3">Bhandari2020-Ext</th>
<th colspan="3">Bhandari2020-Mix</th>
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
</tr>
<tr>
<td>SUPERT</td>
<td>0.06</td>
<td>0.31</td>
<td>0.19</td>
<td>0.64</td>
<td>0.42</td>
<td>0.33</td>
<td>0.31</td>
<td>0.61</td>
<td>0.41</td>
</tr>
</table>

## References
[1] Yang Gao, Wei Zhao, and Steffen Eger. [SUPERT: Towards New Frontiers in Unsupervised Evaluation Metrics for Multi-Document Summarization](https://arxiv.org/abs/2005.03724). ACL, 2020.