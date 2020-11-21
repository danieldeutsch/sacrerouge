# Modified file from https://github.com/Yale-LILY/SummEval/blob/master/data_processing/pair_data.py
"""
Script for recreating the full model outputs from CNN/DM Story files.
CNN/DM Story files can be downloaded from https://cs.nyu.edu/~kcho/DMQA/
"""
import argparse
import json
import os
from tqdm import tqdm
from glob import glob


def parse_story_file(content):
    """
    Remove article highlights and unnecessary white characters.
    """
    content_raw = content.split("@highlight")[0]
    content = " ".join(filter(None, [x.strip() for x in content_raw.split("\n")]))
    return content

def annotation_pairing(data_annotations, story_files):
    print("Processing file:", data_annotations)
    with open(data_annotations) as fd:
        dataset = [json.loads(line) for line in fd]

    for example in dataset:
        story_path = os.path.join(story_files, example["filepath"])

        with open(story_path) as fd:
            story_content = fd.read()
            example["text"] = parse_story_file(story_content)

    paired_file = data_annotations.replace("aligned", "aligned.paired")
    if os.path.dirname(paired_file):
        os.makedirs(os.path.dirname(paired_file), exist_ok=True)
    with open(paired_file, "w") as fd:
        for example in dataset:
            fd.write(json.dumps(example, ensure_ascii=False) + "\n")


def output_pairing(aligned_data, story_files, model_outputs):
    """
    Walk data sub-directories and recreate examples
    """
    for unpaired_path in glob(f'{aligned_data}/*/aligned/*'):
        filename = os.path.basename(unpaired_path)

        if not (".jsonl" in filename and "aligned" in filename and os.path.isfile(unpaired_path)):
            continue

        print("Processing file:", unpaired_path)
        with open(unpaired_path) as fd:
            dataset = [json.loads(line) for line in fd]

        for example in tqdm(dataset):
            story_path = os.path.join(story_files, example["filepath"])

            with open(story_path) as fd:
                story_content = fd.read()
                example["text"] = parse_story_file(story_content)

        paired_filename = filename.replace("aligned", "aligned.paired")
        paired_path = os.path.join(model_outputs, "paired", paired_filename)
        os.makedirs(os.path.dirname(paired_path), exist_ok=True)
        with open(paired_path, "w") as fd:
            for example in dataset:
                fd.write(json.dumps(example, ensure_ascii=False) + "\n")


def run_pair_data(data_annotations: str = None, model_outputs: str = None, story_files: str = None):
    if not (data_annotations or model_outputs) or not story_files:
            raise RuntimeError("To run script please specify `data_annotations` to pair human annotation data or"
                               "`model_outputs` to pair generated summaries. Story files should be specified in either case.")

    if model_outputs:
        aligned_data = model_outputs # os.path.join(model_outputs, "aligned")

    if data_annotations:
        annotation_pairing(data_annotations, story_files)

    if model_outputs and story_files:
        output_pairing(aligned_data, story_files, model_outputs)

# if __name__ == "__main__":
#     PARSER = argparse.ArgumentParser()
#     PARSER.add_argument("--data_annotations", type=str, help="Path to file human annotations")
#     PARSER.add_argument("--model_outputs", type=str, help="Path to directory holding model data")
#     PARSER.add_argument("--story_files", type=str, help="Path to directory holding CNNDM story files")
#     ARGS = PARSER.parse_args()
#
#
#     if not (ARGS.data_annotations or ARGS.model_outputs) or not ARGS.story_files:
#         raise RuntimeError("To run script please specify `data_annotations` to pair human annotation data or"
#                            "`model_outputs` to pair generated summaries. Story files should be specified in either case.")
#
#     if ARGS.model_outputs:
#         ARGS.aligned_data = os.path.join(ARGS.model_outputs, "aligned")
#
#     if ARGS.data_annotations:
#         annotation_pairing(ARGS)
#
#     if ARGS.model_outputs and ARGS.story_files:
#         output_pairing(ARGS)