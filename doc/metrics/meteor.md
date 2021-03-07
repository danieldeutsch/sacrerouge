# METEOR
METEOR [1] is a reference-based metric that scores a summary based on an alignment to the reference.
Our implementation wraps the released Java library.
The name for this metric is `meteor`.

## Setting Up
METEOR requires Java (not sure which version) to run.
It can be set up with the following command:
```bash
sacrerouge setup-metric meteor
```

To verify your installation, run:
```bash
pytest sacrerouge/tests/metrics/meteor_test.py
```

## Correlations
Here are the correlations of METEOR as implemented in SacreROUGE to the "overall responsiveness" human judgments on several datasets.

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
<td>METEOR</td>
<td>0.50</td>
<td>0.50</td>
<td>0.40</td>
<td>0.55</td>
<td>0.51</td>
<td>0.41</td>
<td>0.66</td>
<td>0.66</td>
<td>0.54</td>
<td>0.60</td>
<td>0.52</td>
<td>0.42</td>
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
<td>METEOR</td>
<td>0.60</td>
<td>0.57</td>
<td>0.46</td>
<td>0.56</td>
<td>0.58</td>
<td>0.46</td>
<td>0.71</td>
<td>0.72</td>
<td>0.59</td>
<td>0.61</td>
<td>0.56</td>
<td>0.46</td>
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
<td>METEOR</td>
<td>0.80</td>
<td>0.80</td>
<td>0.61</td>
<td>0.81</td>
<td>0.81</td>
<td>0.63</td>
<td>0.91</td>
<td>0.93</td>
<td>0.81</td>
<td>0.93</td>
<td>0.77</td>
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
<td>METEOR</td>
<td>0.89</td>
<td>0.86</td>
<td>0.69</td>
<td>0.69</td>
<td>0.87</td>
<td>0.71</td>
<td>0.89</td>
<td>0.95</td>
<td>0.85</td>
<td>0.76</td>
<td>0.85</td>
<td>0.68</td>
</tr>
</table>

Here are the correlations to the annotations provided by Bhandari et al., (2020).
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
<td>METEOR</td>
<td>0.67</td>
<td>0.64</td>
<td>0.52</td>
<td>0.25</td>
<td>0.22</td>
<td>0.18</td>
<td>0.53</td>
<td>0.50</td>
<td>0.40</td>
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
<td>METEOR</td>
<td>0.96</td>
<td>0.93</td>
<td>0.82</td>
<td>0.66</td>
<td>0.60</td>
<td>0.47</td>
<td>0.95</td>
<td>0.95</td>
<td>0.84</td>
</tr>
</table>

## References
[1] Michael Denkowski and Alon Lavie. "[Meteor Universal: Language Specific Translation Evaluation for Any Target Language.](https://www.cs.cmu.edu/~alavie/METEOR/pdf/meteor-1.5.pdf)" WMT 2014.