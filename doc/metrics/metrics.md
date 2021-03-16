# Evaluation Metrics
SacreROUGE wraps the original implementations of many different evaluation metrics.
The following metrics have been implemented:

- [APES](apes.md)
- [AutoSummENG, MeMoG, and NPoWER](autosummeng.md)
- [BERTScore](bertscore.md)
- [BEwT-E](bewte.md)
- [BLANC](blanc.md)
- [Decomposed ROUGE](decomposed-rouge.md)
- [METEOR](meteor.md)
- [MoverScore](moverscore.md)
- [Pyramid Score](pyramid-score.md)
- [PyrEval](pyreval.md)
- [QAEval](qaeval.md)
- [ROUGE](rouge.md) and a [Python-based implementation](python-rouge.md)
- [S3](s3.md)
- [SIMetrix](simetrix.md)
- [Sum-QE](sumqe.md)
- [SUPERT](supert.md)
    
For specific details about the metrics, please refer to their corresponding documentation.

When using SacreROUGE to set up each metric, any necessary data or software dependencies are saved to `$SACREROUGE_DATA_ROOT` which defaults to `~/.sacrerouge`.