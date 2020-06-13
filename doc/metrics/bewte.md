# BEwT-E
BEwT-E [1] is an extension of the Basic Elements [2].
These metrics compare a summary and reference based on matches between heads of syntactic phrases and dependency tree-based relations.
Our implementation wraps a [mavenized fork](https://github.com/igorbrigadir/ROUGE-BEwTE) of the original code.

## Setting Up
Running BEwT-E requires having Git LFS, Java 1.6, and Maven installed.
Then, it can be set up with the following command:
```bash
sacrerouge setup-metric bewte
```

## References
[1] Stephen Tratz and Eduard Hovy. [BEwT­E: Basic Elements with Transformations for Evaluation](http://www.cs.cmu.edu/~./hovy/papers/08MetricsMATR-BEwT-E.pdf).

[2] Eduard Hovy, Chin-Yew Lin, Liang Zhou, and Junichi Fukumoto. [Automated Summarization Evaluation with Basic Elements](http://www.lrec-conf.org/proceedings/lrec2006/pdf/438_pdf.pdf). LREC 2006