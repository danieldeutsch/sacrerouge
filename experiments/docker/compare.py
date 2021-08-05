import argparse
import json
import pytest
from typing import Dict, List, Tuple, Union

NestedDict = Union[Dict[str, float], "NestedDict"]


def flatten_nested_dict(nested_dict: NestedDict) -> Dict[Tuple[str, ...], float]:
    def _recursively_flatten(
        target: Dict[Tuple[str, ...], float], d: NestedDict, prefix: List[str]
    ) -> Dict[Tuple[str, ...], float]:
        for key, value in d.items():
            if isinstance(value, dict):
                _recursively_flatten(target, value, prefix + [key])
            else:
                target[tuple(prefix + [key])] = value
        return target

    return _recursively_flatten({}, nested_dict, [])


def assert_dicts_approx_equal(
    d1: NestedDict, d2: NestedDict, rel: float = None, abs: float = None
):
    d1 = flatten_nested_dict(d1)
    d2 = flatten_nested_dict(d2)
    assert d1.keys() == d2.keys()
    for key in d1.keys():
        assert d1[key] == pytest.approx(d2[key], rel=rel, abs=abs), (key, d1[key], d2[key])


def load_scores(input_file: str):
    scores_dict = {}
    with open(input_file, "r") as f:
        for line in f:
            instance = json.loads(line)
            scores_dict[(instance["instance_id"], instance["summarizer_id"])] = instance
    return scores_dict


def main(args):
    original = load_scores(args.original)
    docker = load_scores(args.docker)

    assert len(original) == len(docker)
    for key in original.keys():
        assert_dicts_approx_equal(original[key]["metrics"], docker[key]["metrics"], abs=1e-4)
    print("Equal", args.original, args.docker)


if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument("--original", required=True)
    argp.add_argument("--docker", required=True)
    args = argp.parse_args()
    main(args)