{
  "dataset_reader": {
    "type": "summary-only"
  },
  "metrics": [
    {
      "type": "sum-qe",
      "environment_name": "/shared/ddeutsch/envs/SumQE2",
      "model_file": std.extVar("MODEL_FILE"),
      "verbose": true
    }
  ]
}
