# Pyramid Score
The Pyramid Score is a manual evaluation metric for summarization that scores a summary by identifying summary content units it has in common with a set of reference summaries. [1]
Given a Pyramid annotation of a system summary and Pyramid created from reference summaries, our implementation will calculate the modified pyramid score. [2]
The modified pyramid score for a system summary is the ratio between the total weight of the SCUs in the summary and the total weight of the best possible summary.
The ideal summary has the number of SCUs equal to the average of the number of SCUs in the summaries used to create the Pyramid.
Then unique SCUs are selected in decreasing order until the number of selected SCUs is equal to the average length.    

The name for this metric is `pyramid-score`.

## Correlations
Here are the correlations of our implementation of the modified pyramid score "overall responsiveness" human judgments on several datasets.
The DUC/TAC datasets come with the modified pyramid score already calculated, but these numbers are based on our recalculation of the score using the Pyramids directly.

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
<td>ModifiedPyramidScore</td>
<td>0.59</td>
<td>0.59</td>
<td>0.50</td>
<td>0.59</td>
<td>0.57</td>
<td>0.48</td>
<td>0.81</td>
<td>0.81</td>
<td>0.71</td>
<td>0.63</td>
<td>0.62</td>
<td>0.52</td>
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
<td>ModifiedPyramidScore</td>
<td>0.71</td>
<td>0.66</td>
<td>0.55</td>
<td>0.72</td>
<td>0.64</td>
<td>0.54</td>
<td>0.86</td>
<td>0.85</td>
<td>0.75</td>
<td>0.74</td>
<td>0.69</td>
<td>0.58</td>
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
<td>ModifiedPyramidScore</td>
<td>0.90</td>
<td>0.88</td>
<td>0.70</td>
<td>0.90</td>
<td>0.87</td>
<td>0.70</td>
<td>0.99</td>
<td>0.95</td>
<td>0.84</td>
<td>0.93</td>
<td>0.85</td>
<td>0.66</td>
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
<td>ModifiedPyramidScore</td>
<td>0.97</td>
<td>0.92</td>
<td>0.76</td>
<td>0.97</td>
<td>0.91</td>
<td>0.76</td>
<td>0.99</td>
<td>0.97</td>
<td>0.89</td>
<td>0.98</td>
<td>0.90</td>
<td>0.74</td>
</tr>
</table>

## Original Correlations
Here are the correlations of our calculated score to the original scores reported by DUC/TAC.
These numbers demonstrate the fidelity of the implementation.

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
<td>ModifiedPyramidScore</td>
<td>1.00</td>
<td>1.00</td>
<td>0.99</td>
<td>1.00</td>
<td>1.00</td>
<td>1.00</td>
<td>1.00</td>
<td>1.00</td>
<td>1.00</td>
<td>1.00</td>
<td>1.00</td>
<td>1.00</td>
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
<td>ModifiedPyramidScore</td>
<td>1.00</td>
<td>1.00</td>
<td>0.98</td>
<td>1.00</td>
<td>1.00</td>
<td>0.99</td>
<td>1.00</td>
<td>1.00</td>
<td>0.99</td>
<td>1.00</td>
<td>1.00</td>
<td>0.99</td>
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
<td>ModifiedPyramidScore</td>
<td>1.00</td>
<td>1.00</td>
<td>0.99</td>
<td>1.00</td>
<td>1.00</td>
<td>0.99</td>
<td>1.00</td>
<td>1.00</td>
<td>0.99</td>
<td>1.00</td>
<td>1.00</td>
<td>0.99</td>
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
<td>ModifiedPyramidScore</td>
<td>1.00</td>
<td>1.00</td>
<td>0.99</td>
<td>1.00</td>
<td>1.00</td>
<td>0.99</td>
<td>1.00</td>
<td>1.00</td>
<td>0.99</td>
<td>1.00</td>
<td>1.00</td>
<td>0.99</td>
</tr>
</table>
__

## References
[1] Ani Nenkova and Rebecca J. Passonneau. [Evaluating Content Selection in Summarization: The Pyramid Method](https://www.aclweb.org/anthology/N04-1019). 2004.
[2] Rebecca J. Passonneau. [Formal and functional assessment of the pyramid method for summary content evaluation](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.521.778&rep=rep1&type=pdf). 2009.