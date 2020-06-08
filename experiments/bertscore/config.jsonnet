{
  "dataset_reader": {
    "type": "reference-based"
  },
  "metrics": [
    {
      "type": "bertscore",
      "idf": std.extVar("IDF") == "true"
    }
  ]
}
