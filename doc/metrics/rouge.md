# ROUGE
ROUGE [1] is a reference-based evaluation based on n-gram overlaps between a summary and its reference.
Our implementation wraps the original Perl code.

## Setting Up
To set up ROUGE, run the following:
```bash
sacrerouge setup-metric rouge
```

To verify your installation, run:
```bash
pytest sacrerouge/tests/metrics/rouge_test.py
```
If the unit tests fail, it could be because the necessary Perl libraries aren't installed ROUGE WordNet exceptions file needs to be recreated.
To install the Perl libraries, run:
```bash
sudo apt-get install libxml-dom-perl
# or
sudo cpan install XML::DOM
```
To recreate the database file, run:
```bash
# $SACREROUGE_DATA_ROOT defaults to ~/.sacrerouge
cd $SACREROUGE_DATA_ROOT/metrics/ROUGE-1.5.5/data/WordNet-2.0-Exceptions
./buildExeptionDB.pl . exc WordNet-2.0.exc.db
cd ..
rm WordNet-2.0.exc.db
ln -s WordNet-2.0-Exceptions/WordNet-2.0.exc.db WordNet-2.0.exc.db
```

## References
[1] Chin-Yew Lin. [ROUGE: A Package for Automatic Evaluation of Summaries](https://www.aclweb.org/anthology/W04-1013/). 2004.