# BEwT-E
BEwT-E [1] is an extension of the Basic Elements [2].
These metrics compare a summary and reference based on matches between heads of syntactic phrases and dependency tree-based relations.
Our implementation wraps a [mavenized fork](https://github.com/igorbrigadir/ROUGE-BEwTE) of the original code.
The name for this metric is `bewte`.

## Setting Up
Running BEwT-E requires having Java 1.6 and Maven installed.
Then, it can be set up with the following command:
```bash
sacrerouge setup-metric bewte
```

To verify your installation, run:
```bash
pytest sacrerouge/tests/metrics/bewte_test.py
```

## Correlations
Here are the correlations of BEwT-E as implemented in SacreROUGE to the "overall responsiveness" human judgments on several datasets.

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
<td>BEwTE-P</td>
<td>-0.22</td>
<td>-0.20</td>
<td>-0.16</td>
<td>-0.20</td>
<td>-0.19</td>
<td>-0.14</td>
<td>0.08</td>
<td>-0.07</td>
<td>-0.06</td>
<td>0.28</td>
<td>-0.01</td>
<td>-0.01</td>
</tr>
<tr>
<td>BEwTE-R</td>
<td>0.50</td>
<td>0.49</td>
<td>0.39</td>
<td>0.53</td>
<td>0.50</td>
<td>0.40</td>
<td>0.66</td>
<td>0.62</td>
<td>0.51</td>
<td>0.59</td>
<td>0.51</td>
<td>0.41</td>
</tr>
<tr>
<td>BEwTE-F1</td>
<td>0.49</td>
<td>0.47</td>
<td>0.38</td>
<td>0.56</td>
<td>0.49</td>
<td>0.39</td>
<td>0.66</td>
<td>0.62</td>
<td>0.50</td>
<td>0.59</td>
<td>0.50</td>
<td>0.40</td>
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
<td>BEwTE-P</td>
<td>-0.24</td>
<td>-0.23</td>
<td>-0.18</td>
<td>-0.18</td>
<td>-0.20</td>
<td>-0.15</td>
<td>0.05</td>
<td>-0.12</td>
<td>-0.10</td>
<td>0.24</td>
<td>-0.04</td>
<td>-0.04</td>
</tr>
<tr>
<td>BEwTE-R</td>
<td>0.60</td>
<td>0.56</td>
<td>0.45</td>
<td>0.54</td>
<td>0.55</td>
<td>0.44</td>
<td>0.72</td>
<td>0.69</td>
<td>0.57</td>
<td>0.59</td>
<td>0.54</td>
<td>0.44</td>
</tr>
<tr>
<td>BEwTE-F1</td>
<td>0.58</td>
<td>0.55</td>
<td>0.45</td>
<td>0.58</td>
<td>0.55</td>
<td>0.44</td>
<td>0.71</td>
<td>0.68</td>
<td>0.56</td>
<td>0.59</td>
<td>0.53</td>
<td>0.43</td>
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
<td>BEwTE-P</td>
<td>-0.77</td>
<td>-0.68</td>
<td>-0.50</td>
<td>-0.64</td>
<td>-0.57</td>
<td>-0.47</td>
<td>0.39</td>
<td>-0.48</td>
<td>-0.38</td>
<td>0.68</td>
<td>-0.42</td>
<td>-0.32</td>
</tr>
<tr>
<td>BEwTE-R</td>
<td>0.84</td>
<td>0.82</td>
<td>0.63</td>
<td>0.80</td>
<td>0.80</td>
<td>0.63</td>
<td>0.91</td>
<td>0.85</td>
<td>0.73</td>
<td>0.92</td>
<td>0.75</td>
<td>0.58</td>
</tr>
<tr>
<td>BEwTE-F1</td>
<td>0.84</td>
<td>0.80</td>
<td>0.62</td>
<td>0.87</td>
<td>0.81</td>
<td>0.63</td>
<td>0.90</td>
<td>0.86</td>
<td>0.73</td>
<td>0.91</td>
<td>0.73</td>
<td>0.57</td>
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
<td>BEwTE-P</td>
<td>-0.65</td>
<td>-0.75</td>
<td>-0.57</td>
<td>-0.46</td>
<td>-0.59</td>
<td>-0.47</td>
<td>0.14</td>
<td>-0.58</td>
<td>-0.47</td>
<td>0.36</td>
<td>-0.49</td>
<td>-0.39</td>
</tr>
<tr>
<td>BEwTE-R</td>
<td>0.91</td>
<td>0.87</td>
<td>0.71</td>
<td>0.71</td>
<td>0.87</td>
<td>0.70</td>
<td>0.92</td>
<td>0.91</td>
<td>0.79</td>
<td>0.79</td>
<td>0.83</td>
<td>0.67</td>
</tr>
<tr>
<td>BEwTE-F1</td>
<td>0.90</td>
<td>0.87</td>
<td>0.71</td>
<td>0.78</td>
<td>0.87</td>
<td>0.70</td>
<td>0.90</td>
<td>0.91</td>
<td>0.79</td>
<td>0.76</td>
<td>0.82</td>
<td>0.66</td>
</tr>
</table>

## References
[1] Stephen Tratz and Eduard Hovy. [BEwT­E: Basic Elements with Transformations for Evaluation](http://www.cs.cmu.edu/~./hovy/papers/08MetricsMATR-BEwT-E.pdf).

[2] Eduard Hovy, Chin-Yew Lin, Liang Zhou, and Junichi Fukumoto. [Automated Summarization Evaluation with Basic Elements](http://www.lrec-conf.org/proceedings/lrec2006/pdf/438_pdf.pdf). LREC 2006