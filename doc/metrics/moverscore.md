# MoverScore
MoverScore [1] is a reference-based evaluation metric using an Earth Mover's Distance between a summary and its reference that uses contextual word representations.
Our implementation uses the `moverscore` [pip package](https://github.com/AIPHES/emnlp19-moverscore).

## Setting Up
To set up MoverScore, pip install the package:
```bash
pip3 install moverscore
```
There are currently several libraries which also should be installed and won't be installed with the pip command, so please try to import `moverscore_v2` in a Python terminal to verify it is installed.

Then, some data dependencies can be downloaded via:
```bash
sacrerouge setup-metric moverscore
```

To verify your installation, run:
```bash
pytest sacrerouge/tests/metrics/moverscore_test.py
```

## Correlations
Here are the correlations of MoverScore as implemented in SacreROUGE to the "overall responsiveness" human judgments on several datasets.

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
<td>MoverScore</td>
<td>0.50</td>
<td>0.49</td>
<td>0.40</td>
<td>0.51</td>
<td>0.52</td>
<td>0.42</td>
<td>0.57</td>
<td>0.63</td>
<td>0.52</td>
<td>-0.28</td>
<td>0.30</td>
<td>0.25</td>
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
<td>MoverScore</td>
<td>0.60</td>
<td>0.56</td>
<td>0.46</td>
<td>0.54</td>
<td>0.58</td>
<td>0.47</td>
<td>0.61</td>
<td>0.70</td>
<td>0.58</td>
<td>-0.20</td>
<td>0.36</td>
<td>0.31</td>
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
<td>MoverScore</td>
<td>0.83</td>
<td>0.82</td>
<td>0.63</td>
<td>0.82</td>
<td>0.80</td>
<td>0.63</td>
<td>0.81</td>
<td>0.81</td>
<td>0.67</td>
<td>-0.63</td>
<td>0.59</td>
<td>0.49</td>
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
<td>MoverScore</td>
<td>0.91</td>
<td>0.88</td>
<td>0.71</td>
<td>0.77</td>
<td>0.86</td>
<td>0.69</td>
<td>0.80</td>
<td>0.88</td>
<td>0.75</td>
<td>-0.28</td>
<td>0.68</td>
<td>0.59</td>
</tr>
</table>

## References
[1] Wei Zhao, Maxime Peyrard, Fei Liu, Yang Gao, Christian M. Meyer, and Steffen Eger. [MoverScore: Text Generation Evaluating with Contextualized Embeddings and Earth Mover Distance](https://www.aclweb.org/anthology/D19-1053/). EMNLP 2019.