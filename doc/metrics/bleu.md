# BLEU
Our BLEU implementation is a wrapper around [SacreBLEU](https://github.com/mjpost/sacrebleu).
Although BLEU was intended to be a corpus-level metric, we have only implemented the sentence-level version.
See `sacrebleu.BLEU` for details.
The metric is registered under the name `sent-bleu`.

## Setting Up
No setup is required.

## Correlations
Here are the correlations of SentBLEU to overall responsiveness correlations on the TAC datasets:

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
<td>SentBLEU</td>
<td>0.39</td>
<td>0.41</td>
<td>0.33</td>
<td>0.41</td>
<td>0.47</td>
<td>0.37</td>
<td>0.56</td>
<td>0.56</td>
<td>0.46</td>
<td>0.44</td>
<td>0.43</td>
<td>0.35</td>
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
<td>SentBLEU</td>
<td>0.45</td>
<td>0.45</td>
<td>0.36</td>
<td>0.36</td>
<td>0.48</td>
<td>0.38</td>
<td>0.57</td>
<td>0.59</td>
<td>0.47</td>
<td>0.42</td>
<td>0.43</td>
<td>0.34</td>
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
<td>SentBLEU</td>
<td>0.85</td>
<td>0.87</td>
<td>0.68</td>
<td>0.61</td>
<td>0.83</td>
<td>0.66</td>
<td>0.96</td>
<td>0.92</td>
<td>0.78</td>
<td>0.92</td>
<td>0.78</td>
<td>0.59</td>
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
<td>SentBLEU</td>
<td>0.87</td>
<td>0.90</td>
<td>0.74</td>
<td>0.41</td>
<td>0.88</td>
<td>0.71</td>
<td>0.92</td>
<td>0.94</td>
<td>0.81</td>
<td>0.71</td>
<td>0.77</td>
<td>0.60</td>
</tr>
</table>

Here are the correlations of SentBLEU to the annotations in Fabbri et al. (2020):

Summary-level, peers only:
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
<td>SentBLEU</td>
<td>0.16</td>
<td>0.15</td>
<td>0.11</td>
</tr>
</table>

System-level, peers only:
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
<td>SentBLEU</td>
<td>0.50</td>
<td>0.35</td>
<td>0.20</td>
</tr>
</table>

Here are the correlations to the annotations collected by Bhandari et al. (2020):
Summary-level, peers only:
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
<td>SentBLEU</td>
<td>0.39</td>
<td>0.38</td>
<td>0.30</td>
<td>0.16</td>
<td>0.16</td>
<td>0.14</td>
<td>0.28</td>
<td>0.26</td>
<td>0.20</td>
</tr>
</table>

System-level, peers only:
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
<td>SentBLEU</td>
<td>0.41</td>
<td>0.52</td>
<td>0.36</td>
<td>-0.13</td>
<td>-0.07</td>
<td>-0.05</td>
<td>0.26</td>
<td>0.32</td>
<td>0.21</td>
</tr>
</table>