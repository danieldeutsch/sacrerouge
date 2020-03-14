# ROUGE-WE
This is a wrapper around the official [ROUGE-WE code](https://github.com/ng-j-p/rouge-we).
At this time, we have decided to not continue the integration into our repository because the original code has bugs which cause non-deterministic results (see [here](https://github.com/ng-j-p/rouge-we/issues/1) for more details).

## Setup
First, you have to create the python2.7 environment that will be used to run the word vector server.
```
conda env create -n rouge-we -f environment.yml
```
Then, download the [GoogleNews vectors](https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit?usp=sharing) to `GoogleNews-vectors-negative300.bin.gz` in this directory.
Next, clone the ROUGE-WE code
```
git clone https://github.com/ng-j-p/rouge-we
```

To test your setup, `cd` into the `rouge-we` directory and run the following:
```
conda activate rouge-we
python word2vec_server.m.py -m ../GoogleNews-vectors-negative300.bin.gz

# In another shell after the server initializes
perl ROUGE-WE-1.0.0.pl -x -n 2 -U -2 4 -e rouge_1.5.5_data/ -c 95 -a sample-config.xml
```
If the perl script has an error about "Can't locate JSON.pm", run `cpanm install JSON` and try again.
