# PyrEval
PyrEval [1] is an evaluation metric that automates the construction of a Pyramid and scoring a candidate summary.
The SacreROUGE implementation wraps [our modification](https://github.com/danieldeutsch/PyrEval) or the [original source code](https://github.com/serenayj/PyrEval) which fixed an infinite loop error we encountered.

Currently, the score from the original code [depends on the order of the reference summaries](https://github.com/serenayj/PyrEval/issues/7).
To mitigate this, we sort all of the reference summaries alphabetically before passing them to PyrEval, so the results should be deterministic.
However, because the PyrEval uses `glob` to load files and whether or not they are sorted by default is system-specific, we have seen differences in scores across platforms.

Since the intermediate processing files in PyrEval are saved in the original code directory, only one PyrEval process can be running on a machine at a time.

The name for this metric is `PyrEval`.

## Setting Up
Since the original code is written in Python 2.7, running PyrEval requires creating a conda environment.
We used the following `requirements.txt`:
```
nltk==3.4.5
scikit-learn
beautifulsoup4==4.8.2
numpy==1.16.6
scipy==1.2.3
networkx==2.2
statistics==1.0.3.5
pandas==0.24.2
theano==1.0.4
lxml==4.5.0
```
The name of the environment needs to be passed as `environment_name` to the constructor of the `PyrEval` class.
Further, the environment variable `CONDA_INIT` must be set to the conda initialization script (`<conda-root>/etc/profile.d/conda.sh`).

To set up the metric, run
```bash
sacrerouge setup-metric pyreval
```
It requires Java to be installed.

To verify your installation, set the environment variable `PYREVAL_ENV` to be the name of the conda environment, then run:
```
pytest sacrerouge/tests/metrics/pyreval_test.py
```
However, because of the `glob` issue mentioned above, the test may not pass.

## Correlations
Here are the correlations of the different PyrEval outputs to the "overall responsiveness" human judgments on several datasets.

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
<td>Raw</td>
<td>0.28</td>
<td>0.28</td>
<td>0.23</td>
<td>0.41</td>
<td>0.36</td>
<td>0.29</td>
<td>0.50</td>
<td>0.48</td>
<td>0.41</td>
<td>0.43</td>
<td>0.38</td>
<td>0.32</td>
</tr>
<tr>
<td>Quality</td>
<td>0.32</td>
<td>0.32</td>
<td>0.26</td>
<td>0.40</td>
<td>0.35</td>
<td>0.28</td>
<td>0.51</td>
<td>0.50</td>
<td>0.41</td>
<td>0.43</td>
<td>0.36</td>
<td>0.29</td>
</tr>
<tr>
<td>Coverage</td>
<td>0.28</td>
<td>0.28</td>
<td>0.23</td>
<td>0.41</td>
<td>0.36</td>
<td>0.29</td>
<td>0.50</td>
<td>0.48</td>
<td>0.41</td>
<td>0.43</td>
<td>0.38</td>
<td>0.32</td>
</tr>
<tr>
<td>Comprehensive</td>
<td>0.31</td>
<td>0.31</td>
<td>0.25</td>
<td>0.42</td>
<td>0.36</td>
<td>0.28</td>
<td>0.52</td>
<td>0.50</td>
<td>0.40</td>
<td>0.45</td>
<td>0.38</td>
<td>0.31</td>
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
<td>Raw</td>
<td>0.48</td>
<td>0.40</td>
<td>0.32</td>
<td>0.54</td>
<td>0.49</td>
<td>0.39</td>
<td>0.63</td>
<td>0.60</td>
<td>0.49</td>
<td>0.52</td>
<td>0.45</td>
<td>0.37</td>
</tr>
<tr>
<td>Quality</td>
<td>0.41</td>
<td>0.39</td>
<td>0.31</td>
<td>0.44</td>
<td>0.43</td>
<td>0.34</td>
<td>0.58</td>
<td>0.57</td>
<td>0.46</td>
<td>0.44</td>
<td>0.38</td>
<td>0.30</td>
</tr>
<tr>
<td>Coverage</td>
<td>0.48</td>
<td>0.39</td>
<td>0.31</td>
<td>0.54</td>
<td>0.48</td>
<td>0.38</td>
<td>0.62</td>
<td>0.59</td>
<td>0.48</td>
<td>0.52</td>
<td>0.44</td>
<td>0.36</td>
</tr>
<tr>
<td>Comprehensive</td>
<td>0.46</td>
<td>0.41</td>
<td>0.32</td>
<td>0.52</td>
<td>0.48</td>
<td>0.37</td>
<td>0.62</td>
<td>0.60</td>
<td>0.49</td>
<td>0.51</td>
<td>0.43</td>
<td>0.35</td>
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
<td>Raw</td>
<td>0.62</td>
<td>0.58</td>
<td>0.41</td>
<td>0.78</td>
<td>0.60</td>
<td>0.47</td>
<td>0.85</td>
<td>0.81</td>
<td>0.68</td>
<td>0.81</td>
<td>0.65</td>
<td>0.51</td>
</tr>
<tr>
<td>Quality</td>
<td>0.81</td>
<td>0.79</td>
<td>0.60</td>
<td>0.87</td>
<td>0.84</td>
<td>0.66</td>
<td>0.96</td>
<td>0.87</td>
<td>0.70</td>
<td>0.90</td>
<td>0.72</td>
<td>0.54</td>
</tr>
<tr>
<td>Coverage</td>
<td>0.63</td>
<td>0.58</td>
<td>0.41</td>
<td>0.78</td>
<td>0.60</td>
<td>0.46</td>
<td>0.86</td>
<td>0.81</td>
<td>0.68</td>
<td>0.81</td>
<td>0.64</td>
<td>0.50</td>
</tr>
<tr>
<td>Comprehensive</td>
<td>0.75</td>
<td>0.72</td>
<td>0.53</td>
<td>0.84</td>
<td>0.75</td>
<td>0.59</td>
<td>0.93</td>
<td>0.87</td>
<td>0.71</td>
<td>0.89</td>
<td>0.71</td>
<td>0.54</td>
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
<td>Raw</td>
<td>0.90</td>
<td>0.77</td>
<td>0.59</td>
<td>0.80</td>
<td>0.76</td>
<td>0.60</td>
<td>0.91</td>
<td>0.89</td>
<td>0.76</td>
<td>0.79</td>
<td>0.74</td>
<td>0.59</td>
</tr>
<tr>
<td>Quality</td>
<td>0.82</td>
<td>0.88</td>
<td>0.69</td>
<td>0.74</td>
<td>0.90</td>
<td>0.73</td>
<td>0.85</td>
<td>0.90</td>
<td>0.74</td>
<td>0.64</td>
<td>0.67</td>
<td>0.49</td>
</tr>
<tr>
<td>Coverage</td>
<td>0.90</td>
<td>0.76</td>
<td>0.58</td>
<td>0.80</td>
<td>0.76</td>
<td>0.59</td>
<td>0.90</td>
<td>0.88</td>
<td>0.75</td>
<td>0.79</td>
<td>0.74</td>
<td>0.59</td>
</tr>
<tr>
<td>Comprehensive</td>
<td>0.89</td>
<td>0.83</td>
<td>0.65</td>
<td>0.80</td>
<td>0.85</td>
<td>0.68</td>
<td>0.91</td>
<td>0.91</td>
<td>0.77</td>
<td>0.76</td>
<td>0.79</td>
<td>0.62</td>
</tr>
</table>

## References
[1] Gao, Yanjun, Chen Sun, and Rebecca J. Passonneau. "[Automated Pyramid Summarization Evaluation.](https://www.aclweb.org/anthology/K19-1038/)" CoNLL. 2019.