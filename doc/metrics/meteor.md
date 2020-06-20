# METEOR
METEOR [1] is a reference-based metric that scores a summary based on an alignment to the reference.
Our implementation wraps the released Java library.

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

## References
[1] Michael Denkowski and Alon Lavie. "[Meteor Universal: Language Specific Translation Evaluation for Any Target Language.](https://www.cs.cmu.edu/~alavie/METEOR/pdf/meteor-1.5.pdf)" WMT 2014.