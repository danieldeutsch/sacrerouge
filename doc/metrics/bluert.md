# BLEURT
BLEURT [1] is a reference-based metric that scores a summary using a model with a novel pre-training approach.
The name for this metric is `bleurt`.

## Setting Up
First, run the SacreROUGE setup code:
```bash
sacrerouge setup-metric bleurt
```
Then, because BLEURT relies on TensorFlow and you may not want to have TensorFlow installed in the same Python environment that SacreROUGE is installed it, you must manually cd to the BLEURT directory (`$SACREROUGE_DATA_ROOT/metrics/bleurt`) and pip install the library (`pip install .`).
This should be done with whichever conda environment you want to use to run BLEURT.

To verify your installation, run:
```bash
pytest sacrerouge/tests/metrics/bleurt_test.py
```
Successfully running the tests requires having the environment variable `BLEURT_ENV` set to the name of the conda environment you want to use to run BLEURT.

## Correlations
Here are the correlations of BLEURT as implemented in SacreROUGE to the "overall responsiveness" human judgments on several datasets.

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
<td>BLEURT-Base-128-Avg</td>
<td>0.29</td>
<td>0.28</td>
<td>0.22</td>
<td>0.43</td>
<td>0.40</td>
<td>0.31</td>
<td>0.48</td>
<td>0.43</td>
<td>0.34</td>
<td>0.52</td>
<td>0.39</td>
<td>0.32</td>
</tr>
<tr>
<td>BLEURT-Base-128-Max</td>
<td>0.29</td>
<td>0.28</td>
<td>0.22</td>
<td>0.43</td>
<td>0.39</td>
<td>0.30</td>
<td>0.48</td>
<td>0.42</td>
<td>0.34</td>
<td>0.52</td>
<td>0.39</td>
<td>0.32</td>
</tr>
<tr>
<td>BLEURT-Large-512-Avg</td>
<td>0.42</td>
<td>0.41</td>
<td>0.32</td>
<td>0.56</td>
<td>0.49</td>
<td>0.39</td>
<td>0.60</td>
<td>0.59</td>
<td>0.48</td>
<td>0.59</td>
<td>0.51</td>
<td>0.42</td>
</tr>
<tr>
<td>BLEURT-Large-512-Max</td>
<td>0.41</td>
<td>0.40</td>
<td>0.32</td>
<td>0.54</td>
<td>0.49</td>
<td>0.39</td>
<td>0.59</td>
<td>0.58</td>
<td>0.47</td>
<td>0.58</td>
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
<td>BLEURT-Base-128-Avg</td>
<td>0.42</td>
<td>0.37</td>
<td>0.29</td>
<td>0.50</td>
<td>0.47</td>
<td>0.36</td>
<td>0.58</td>
<td>0.53</td>
<td>0.43</td>
<td>0.54</td>
<td>0.46</td>
<td>0.37</td>
</tr>
<tr>
<td>BLEURT-Base-128-Max</td>
<td>0.43</td>
<td>0.38</td>
<td>0.30</td>
<td>0.50</td>
<td>0.47</td>
<td>0.36</td>
<td>0.59</td>
<td>0.53</td>
<td>0.43</td>
<td>0.54</td>
<td>0.46</td>
<td>0.37</td>
</tr>
<tr>
<td>BLEURT-Large-512-Avg</td>
<td>0.55</td>
<td>0.50</td>
<td>0.40</td>
<td>0.60</td>
<td>0.56</td>
<td>0.44</td>
<td>0.66</td>
<td>0.67</td>
<td>0.55</td>
<td>0.62</td>
<td>0.57</td>
<td>0.47</td>
</tr>
<tr>
<td>BLEURT-Large-512-Max</td>
<td>0.55</td>
<td>0.50</td>
<td>0.40</td>
<td>0.57</td>
<td>0.56</td>
<td>0.44</td>
<td>0.66</td>
<td>0.66</td>
<td>0.54</td>
<td>0.61</td>
<td>0.56</td>
<td>0.45</td>
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
<td>BLEURT-Base-128-Avg</td>
<td>0.69</td>
<td>0.67</td>
<td>0.49</td>
<td>0.87</td>
<td>0.85</td>
<td>0.68</td>
<td>0.89</td>
<td>0.91</td>
<td>0.75</td>
<td>0.90</td>
<td>0.73</td>
<td>0.58</td>
</tr>
<tr>
<td>BLEURT-Base-128-Max</td>
<td>0.72</td>
<td>0.69</td>
<td>0.51</td>
<td>0.89</td>
<td>0.84</td>
<td>0.67</td>
<td>0.89</td>
<td>0.90</td>
<td>0.74</td>
<td>0.90</td>
<td>0.74</td>
<td>0.59</td>
</tr>
<tr>
<td>BLEURT-Large-512-Avg</td>
<td>0.70</td>
<td>0.66</td>
<td>0.47</td>
<td>0.89</td>
<td>0.87</td>
<td>0.71</td>
<td>0.88</td>
<td>0.92</td>
<td>0.77</td>
<td>0.93</td>
<td>0.74</td>
<td>0.57</td>
</tr>
<tr>
<td>BLEURT-Large-512-Max</td>
<td>0.71</td>
<td>0.68</td>
<td>0.48</td>
<td>0.82</td>
<td>0.88</td>
<td>0.72</td>
<td>0.89</td>
<td>0.91</td>
<td>0.75</td>
<td>0.93</td>
<td>0.74</td>
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
<td>BLEURT-Base-128-Avg</td>
<td>0.86</td>
<td>0.77</td>
<td>0.59</td>
<td>0.86</td>
<td>0.90</td>
<td>0.74</td>
<td>0.91</td>
<td>0.94</td>
<td>0.80</td>
<td>0.73</td>
<td>0.82</td>
<td>0.68</td>
</tr>
<tr>
<td>BLEURT-Base-128-Max</td>
<td>0.88</td>
<td>0.79</td>
<td>0.61</td>
<td>0.87</td>
<td>0.89</td>
<td>0.73</td>
<td>0.93</td>
<td>0.94</td>
<td>0.80</td>
<td>0.75</td>
<td>0.83</td>
<td>0.69</td>
</tr>
<tr>
<td>BLEURT-Large-512-Avg</td>
<td>0.90</td>
<td>0.77</td>
<td>0.59</td>
<td>0.83</td>
<td>0.91</td>
<td>0.76</td>
<td>0.87</td>
<td>0.95</td>
<td>0.82</td>
<td>0.79</td>
<td>0.83</td>
<td>0.67</td>
</tr>
<tr>
<td>BLEURT-Large-512-Max</td>
<td>0.90</td>
<td>0.78</td>
<td>0.60</td>
<td>0.76</td>
<td>0.92</td>
<td>0.76</td>
<td>0.88</td>
<td>0.95</td>
<td>0.80</td>
<td>0.80</td>
<td>0.83</td>
<td>0.67</td>
</tr>
</table>

## References
[1] Thibault Sellam, Dipanjan Das, and Ankur P. Parikh. "[BLEURT: Learning Robust Metrics for Text Generation.](https://www.aclweb.org/anthology/2020.acl-main.704.pdf)" ACL 2020.