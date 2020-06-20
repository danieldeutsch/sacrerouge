# Sum-QE
Sum-QE [1] is a BERT-based model to estimate the linguistic quality of a summary.
Our implementation wraps [our fork](https://github.com/danieldeutsch/SumQE) of the [original code](https://github.com/nlpaueb/SumQE) which creates a more compatible command-line interface.
We additionally followed the steps in the repository to retrain their multi-task 5 models which we have saved on AWS:

- [Model trained on DUC 2005 and 2006](https://danieldeutsch.s3.amazonaws.com/sacrerouge/metrics/SumQE/models/multitask_5-duc2005_duc2006.npy)
- [Model trained on DUC 2005 and 2007](https://danieldeutsch.s3.amazonaws.com/sacrerouge/metrics/SumQE/models/multitask_5-duc2005_duc2007.npy)
- [Model trained on DUC 2006 and 2007](https://danieldeutsch.s3.amazonaws.com/sacrerouge/metrics/SumQE/models/multitask_5-duc2006_duc2007.npy)

## Setting Up
Sum-QE has many Python dependencies.
We recommend referencing the repository's instructions for creating the conda environment.
The path to the Python binary can be passed to the `SumQE` class.

The models can be set up with the following command:
```bash
sacrerouge setup-metric sum-qe \
    --download-2005-2006-model \
    --download-2005-2007-model \
    --download-2006-2007-model
```
Each of the `--download` arguments is optional.

To verify your installation, run:
```bash
pytest sacrerouge/tests/metrics/sumqe_test.py
```
This requires setting the environment variable `SUMQE_PYTHON_BINARY` to the Python binary with the Sum-QE dependencies installed.

## Correlations
Here are the correlations of Sum-QE as implemented in SacreROUGE to the "overall responsiveness" human judgments on several datasets.

Summary-level, peers only:
<table>
<tr>
<th></th>
<th colspan="3">DUC2005-Q1</th>
<th colspan="3">DUC2006-Q1</th>
<th colspan="3">DUC2007-Q1</th>
<th colspan="3">DUC2005-Q2</th>
<th colspan="3">DUC2006-Q2</th>
<th colspan="3">DUC2007-Q2</th>
<th colspan="3">DUC2005-Q3</th>
<th colspan="3">DUC2006-Q3</th>
<th colspan="3">DUC2007-Q3</th>
<th colspan="3">DUC2005-Q4</th>
<th colspan="3">DUC2006-Q4</th>
<th colspan="3">DUC2007-Q4</th>
<th colspan="3">DUC2005-Q5</th>
<th colspan="3">DUC2006-Q5</th>
<th colspan="3">DUC2007-Q5</th>
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
<td>SumQE</td>
<td>0.46</td>
<td>0.42</td>
<td>0.33</td>
<td>0.60</td>
<td>0.55</td>
<td>0.44</td>
<td>0.65</td>
<td>0.58</td>
<td>0.47</td>
<td>0.25</td>
<td>0.21</td>
<td>0.17</td>
<td>0.29</td>
<td>0.23</td>
<td>0.19</td>
<td>0.32</td>
<td>0.30</td>
<td>0.24</td>
<td>0.40</td>
<td>0.40</td>
<td>0.31</td>
<td>0.46</td>
<td>0.44</td>
<td>0.35</td>
<td>0.49</td>
<td>0.46</td>
<td>0.37</td>
<td>0.35</td>
<td>0.36</td>
<td>0.28</td>
<td>0.36</td>
<td>0.32</td>
<td>0.25</td>
<td>0.43</td>
<td>0.38</td>
<td>0.31</td>
<td>0.27</td>
<td>0.26</td>
<td>0.21</td>
<td>0.43</td>
<td>0.38</td>
<td>0.30</td>
<td>0.49</td>
<td>0.45</td>
<td>0.36</td>
</tr>
</table>

Summary-level, peers + references:
<table>
<tr>
<th></th>
<th colspan="3">DUC2005-Q1</th>
<th colspan="3">DUC2006-Q1</th>
<th colspan="3">DUC2007-Q1</th>
<th colspan="3">DUC2005-Q2</th>
<th colspan="3">DUC2006-Q2</th>
<th colspan="3">DUC2007-Q2</th>
<th colspan="3">DUC2005-Q3</th>
<th colspan="3">DUC2006-Q3</th>
<th colspan="3">DUC2007-Q3</th>
<th colspan="3">DUC2005-Q4</th>
<th colspan="3">DUC2006-Q4</th>
<th colspan="3">DUC2007-Q4</th>
<th colspan="3">DUC2005-Q5</th>
<th colspan="3">DUC2006-Q5</th>
<th colspan="3">DUC2007-Q5</th>
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
<td>SumQE</td>
<td>0.45</td>
<td>0.40</td>
<td>0.32</td>
<td>0.64</td>
<td>0.60</td>
<td>0.49</td>
<td>0.67</td>
<td>0.62</td>
<td>0.50</td>
<td>0.16</td>
<td>0.12</td>
<td>0.10</td>
<td>0.30</td>
<td>0.25</td>
<td>0.20</td>
<td>0.34</td>
<td>0.33</td>
<td>0.26</td>
<td>0.30</td>
<td>0.30</td>
<td>0.23</td>
<td>0.43</td>
<td>0.42</td>
<td>0.33</td>
<td>0.44</td>
<td>0.40</td>
<td>0.31</td>
<td>0.24</td>
<td>0.26</td>
<td>0.20</td>
<td>0.41</td>
<td>0.37</td>
<td>0.29</td>
<td>0.39</td>
<td>0.34</td>
<td>0.27</td>
<td>0.03</td>
<td>0.06</td>
<td>0.05</td>
<td>0.41</td>
<td>0.39</td>
<td>0.31</td>
<td>0.44</td>
<td>0.41</td>
<td>0.32</td>
</tr>
</table>

System-level, peers only:
<table>
<tr>
<th></th>
<th colspan="3">DUC2005-Q1</th>
<th colspan="3">DUC2006-Q1</th>
<th colspan="3">DUC2007-Q1</th>
<th colspan="3">DUC2005-Q2</th>
<th colspan="3">DUC2006-Q2</th>
<th colspan="3">DUC2007-Q2</th>
<th colspan="3">DUC2005-Q3</th>
<th colspan="3">DUC2006-Q3</th>
<th colspan="3">DUC2007-Q3</th>
<th colspan="3">DUC2005-Q4</th>
<th colspan="3">DUC2006-Q4</th>
<th colspan="3">DUC2007-Q4</th>
<th colspan="3">DUC2005-Q5</th>
<th colspan="3">DUC2006-Q5</th>
<th colspan="3">DUC2007-Q5</th>
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
<td>SumQE</td>
<td>0.81</td>
<td>0.75</td>
<td>0.58</td>
<td>0.92</td>
<td>0.88</td>
<td>0.73</td>
<td>0.92</td>
<td>0.83</td>
<td>0.65</td>
<td>0.41</td>
<td>0.29</td>
<td>0.22</td>
<td>0.69</td>
<td>0.62</td>
<td>0.46</td>
<td>0.71</td>
<td>0.76</td>
<td>0.56</td>
<td>0.68</td>
<td>0.79</td>
<td>0.58</td>
<td>0.92</td>
<td>0.87</td>
<td>0.72</td>
<td>0.92</td>
<td>0.92</td>
<td>0.77</td>
<td>0.71</td>
<td>0.75</td>
<td>0.56</td>
<td>0.89</td>
<td>0.89</td>
<td>0.73</td>
<td>0.90</td>
<td>0.84</td>
<td>0.66</td>
<td>0.54</td>
<td>0.62</td>
<td>0.43</td>
<td>0.86</td>
<td>0.81</td>
<td>0.64</td>
<td>0.87</td>
<td>0.88</td>
<td>0.74</td>
</tr>
</table>

System-level, peers + references:
<table>
<tr>
<th></th>
<th colspan="3">DUC2005-Q1</th>
<th colspan="3">DUC2006-Q1</th>
<th colspan="3">DUC2007-Q1</th>
<th colspan="3">DUC2005-Q2</th>
<th colspan="3">DUC2006-Q2</th>
<th colspan="3">DUC2007-Q2</th>
<th colspan="3">DUC2005-Q3</th>
<th colspan="3">DUC2006-Q3</th>
<th colspan="3">DUC2007-Q3</th>
<th colspan="3">DUC2005-Q4</th>
<th colspan="3">DUC2006-Q4</th>
<th colspan="3">DUC2007-Q4</th>
<th colspan="3">DUC2005-Q5</th>
<th colspan="3">DUC2006-Q5</th>
<th colspan="3">DUC2007-Q5</th>
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
<td>SumQE</td>
<td>0.66</td>
<td>0.63</td>
<td>0.47</td>
<td>0.93</td>
<td>0.91</td>
<td>0.77</td>
<td>0.93</td>
<td>0.88</td>
<td>0.72</td>
<td>-0.30</td>
<td>-0.31</td>
<td>-0.20</td>
<td>0.73</td>
<td>0.72</td>
<td>0.52</td>
<td>0.67</td>
<td>0.76</td>
<td>0.57</td>
<td>0.30</td>
<td>0.49</td>
<td>0.35</td>
<td>0.67</td>
<td>0.74</td>
<td>0.59</td>
<td>0.63</td>
<td>0.55</td>
<td>0.42</td>
<td>0.24</td>
<td>0.44</td>
<td>0.33</td>
<td>0.83</td>
<td>0.88</td>
<td>0.73</td>
<td>0.60</td>
<td>0.58</td>
<td>0.43</td>
<td>-0.20</td>
<td>0.05</td>
<td>0.06</td>
<td>0.64</td>
<td>0.77</td>
<td>0.58</td>
<td>0.57</td>
<td>0.66</td>
<td>0.51</td>
</tr>
</table>

## References
[1] Stratos Xenouleas, Prodromos Malakasiotis, Marianna Apidianaki and Ion Androutsopoulos. [Sum-QE: a BERT-based Summary Quality Estimation Model](https://arxiv.org/abs/1909.00578). EMNLP 2019.