#!/usr/bin/env python
""" A simple script to measure the performance of ofsolver.

    This script only collect results.
    Processing is separate, good for fixing mistakes, without having to rerun
    all tests.
"""

from __future__ import print_function
import subprocess
from timeit import default_timer as time
from os import path
import json
import argparse
import py_global_debug


parser = argparse.ArgumentParser(description='Runs a performance test on ofsolver')
parser.add_argument('test_type',
                    help='The test',
                    choices=["compression", "SATconstraints", "singletable"])
args = parser.parse_args()


PIPELINE_DIR = "../pipelines/"
RULESET_DIR = "../rulesets/"
SOLVER_DIR = "./"
REPEAT = 10
ITERATION_LIMIT = 10000

PIPELINE_DIR = path.relpath(PIPELINE_DIR, SOLVER_DIR)
RULESET_DIR = path.relpath(RULESET_DIR, SOLVER_DIR)


if args.test_type == "singletable":
    BASE_OPTIONS = ["--full", "--single", "--time", "--iterations",
                    str(ITERATION_LIMIT), "--ttp-log-level", "ERROR",
                    "--log-level", "ERROR"]
    OPTIONS = [["--algorithm", "SingleSAT"], ["--algorithm", "SSAT"]]
    PROBLEMS = [
        ["evaluation_contrast_forwarding.pickle", "evaluation_ofdpa_forwarding.json"],
        ["evaluation_ofdpa_forwarding.pickle", "evaluation_contrast_forwarding.json"],
    ]
    OUTPUT = "single-table.json"
elif args.test_type == "compression":
    BASE_OPTIONS = ["--single", "--time", "--iterations",
                    str(ITERATION_LIMIT), "--ttp-log-level", "ERROR",
                    "--log-level", "ERROR", "--algorithm", "SingleSAT"]
    OPTIONS = [["-C"], []]
    PROBLEMS = [
        ["evaluation_ofdpa_gen_0.pickle.bz2", "evaluation_ofdpa_forwarding.json"],
        ["evaluation_ofdpa_gen_1.pickle.bz2", "evaluation_ofdpa_forwarding.json"],
        ["evaluation_ofdpa_gen_3.pickle.bz2", "evaluation_ofdpa_forwarding.json"],
        ["evaluation_ofdpa_gen_5.pickle.bz2", "evaluation_ofdpa_forwarding.json"],
        ["evaluation_ofdpa_gen_10.pickle.bz2", "evaluation_ofdpa_forwarding.json"],
        ["evaluation_ofdpa_gen_20.pickle.bz2", "evaluation_ofdpa_forwarding.json"],
        ["evaluation_ofdpa_gen_30.pickle.bz2", "evaluation_ofdpa_forwarding.json"],
        ["evaluation_ofdpa_gen_50.pickle.bz2", "evaluation_ofdpa_forwarding.json"],
    ]
    OUTPUT = "compression.json"
elif args.test_type == "SATconstraints":
    BASE_OPTIONS = ["--full", "--time", "--single", "--iterations",
                    str(ITERATION_LIMIT), "--ttp-log-level", "ERROR",
                    "--log-level", "ERROR", "--algorithm", "SingleSAT"]
    OPTIONS = ["-oNO_CONFLICT", "-oNO_HIT", "-oNO_MISS",
               "-oNO_PLACEMENT_CONFLICT", "-oNO_PLACEMENT"] # , "-oNO_SAME_TABLE"]

    # OPTIONS are cumulative
    OPTIONS = map(lambda a: OPTIONS[:a], range(len(OPTIONS)+1))

    PROBLEMS = [
        ["evaluation_contrast_forwarding.pickle", "evaluation_ofdpa_forwarding.json"],
        ["evaluation_ofdpa_forwarding.pickle", "evaluation_contrast_forwarding.json"],
    ]
    OUTPUT = "SAT_constraints.json"


# Complete paths
def complete_path(item):
    ruleset, pipeline = item
    return [path.join(RULESET_DIR, ruleset),
            path.join(PIPELINE_DIR, pipeline)]

PROBLEMS = map(complete_path, PROBLEMS)

results = {"problems": []}

for problem in PROBLEMS:
    prob = {"combinations": []}
    results["problems"].append(prob)
    for options in OPTIONS:
        comb = {"repeats": []}
        prob["combinations"].append(comb)
        for repeat in range(REPEAT+1):
            result = {}
            TEST_OPTIONS = options
            result["command"] = "ofsolver"
            result["options"] = BASE_OPTIONS
            result["test_options"] = TEST_OPTIONS
            result["problem"] = problem
            result["run"] = repeat

            command = ["ofsolver"] + BASE_OPTIONS + TEST_OPTIONS + problem
            print(command)
            start_time = time()
            output = subprocess.check_output(command, cwd=SOLVER_DIR)
            total_time = time() - start_time
            print(output)
            result["output"] = output
            result["wall_time"] = total_time

            if repeat == 0:
                # Throw away the first result, as files might not be in memory
                continue
            comb["repeats"].append(result)

with open(OUTPUT, "w") as out:
    json.dump(results, out)
