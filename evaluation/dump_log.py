#!/usr/bin/env python
""" Build a result out of runs """

from __future__ import print_function
import json
import argparse
from collections import defaultdict

parser = argparse.ArgumentParser(description='Process results.')
parser.add_argument('infile', type=argparse.FileType('r'), default="DataSets/without_compression.json")
args = parser.parse_args()

results = json.load(args.infile)

for problem in results["problems"]:
    for combination in problem["combinations"]:
        comb_results = defaultdict(list)
        for result in combination["repeats"]:
            output = result["output"]
            full_command = ([result["command"]] + result["options"] +
                            result["test_options"] + result["problem"])
            print(full_command)
            print(output)
