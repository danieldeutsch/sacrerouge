# Datasets
SacreROUGE provides dataset readers for the following datasets:

- [DUC and TAC](duc-tac/duc-tac.md)
- [MultiLing](multiling/multiling.md)
- [Chaganty 2018](chaganty2018.md)
- [Fabbri 2020](fabbri2020.md)

The readers parse the original data and convert it to a common format for use in SacreROUGE.
Please see the respective documentation for each dataset for more details.

Each of the datasets can be setup via a command such as:
```bash
sacrerouge setup-dataset <dataset-name>
```