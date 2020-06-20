{
  "dataset_reader": {
    "type": "summary-only"
  },
  "metrics": [
    {
      "type": "sum-qe",
      "python_binary": std.extVar("SUMQE_PYTHON_BINARY"),
      "model_file": std.extVar("MODEL_FILE"),
      "verbose": true
    }
  ]
}
