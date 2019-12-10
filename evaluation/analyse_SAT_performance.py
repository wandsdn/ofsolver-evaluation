#!/usr/bin/env python
""" Build a result out of runs """

from __future__ import print_function
import math
import re
from scipy import stats
import json
import argparse
from collections import defaultdict
import to_precision

parser = argparse.ArgumentParser(description='Process results.')
parser.add_argument('infile', type=argparse.FileType('r'))

args = parser.parse_args()

ENABLE_CI95 = True


COUNTERS = [
    "Iterations", "Solutions Checked", "Valid Solutions", "Unique Solutions",
    "Re-actioning Splits Added", "SAT Variables", "SAT Sln Variables", "SAT Clauses",
    "SAT Search Space List", "SAT Search Space"]
TIMERS = ["Total Runtime", "Loading TTP", "Loading Ruleset", "Pre Solve",
          "Compress Ruleset", "Solver Init", "Run Solver",
          "Compute Dependencies", "Generating Transformations",
          "Split Placements", "Direct Placements", "Merge Placements",
          "Re-actioning", "Build SAT Expression", "SAT Solving Time",
          "Init SAT Solver", "Solution Building", "Solution Compare",
          "Post Solve", "Applying Model",
          "Verifying Solution"]
to_collect = COUNTERS + TIMERS

ROW_NAMES = ["Forwarding Conflicts", "Hit Placements", "Table Miss",
             "Placement Conflicts", "Placements", "One Transformation"]

class Stats(object):
    def __init__(self, list):
        if list is None:
            return
        self.data = list
        if len(list) == 0:
            self.min = self.max = self.stdev = self.mean = float('nan')
            self.skew = self.kurt = self.var = float('nan')
            self.CI95 = (float('nan'), float('nan'))
            self.is_sorted = False
            self.n = 0
            self.sem = float('nan')
            return
        self.n, minmax, self.mean, self.var, self.skew, self.kurt = stats.describe(list)
        self.min = minmax[0]
        self.max = minmax[1]
        self.stdev = math.sqrt(self.var)
        self.sem = stats.sem(list)
        self.CI95 = stats.t.interval(0.95, self.n-1, self.mean, self.sem)
        self.data = None

results = json.load(args.infile)

collect_res = ""

for problem in results["problems"]:
    ROWS = ROW_NAMES[:]
    timing_latex = []
    counts_latex = []
    for combination in problem["combinations"]:
        comb_results = defaultdict(list)
        for result in combination["repeats"]:
            output = result["output"]
            full_command = ([result["command"]] + result["options"] +
                            result["test_options"] + result["problem"])
            row = {"Run": result["run"], "Options": " ".join(result["test_options"]),
                   "Wall Time": result["wall_time"]}
            for var in to_collect:
                r = re.compile(r"\n\s*" + re.escape(var) + r": ([0-9., ]+)[^0-9., ]")
                res = r.search(output)
                if res is None:
                    pass
                else:
                    row[var] = res.groups()[0]
                    comb_results[var].append(res.groups()[0])
            comb_results["Wall Time"].append(row["Wall Time"])
            comb_results["Build SAT"].append(
                float(row["Build SAT Expression"]) + float(row["Init SAT Solver"]))
            comb_results["Solve SAT"].append(
                float(row["SAT Solving Time"]) - float(row["Init SAT Solver"]))
            comb_results["Verify"].append(
                float(row["Solution Building"]) + float(row["Solution Compare"]))

        row_name = ROWS[0]
        ROWS = ROWS[1:]
        # For the averages that we want
        calculated = {}
        for k, v in comb_results.items():
            try:
                calculated[k] = Stats(map(float, v))
            except:
                pass
        means = {}
        for k, v in calculated.items():
            means[k] = v.mean

        stddevs = {"Run": "stddev"}
        for k, v in calculated.items():
            stddevs[k] = v.stdev

        CI95s = {"Run": "CI95"}
        for k, v in calculated.items():
            CI95s[k] = v.CI95[1] - v.mean
        def as_2sf(number):
            return to_precision.to_precision(number, 2, notation='std', preserve_integer=True).strip(".")

        def format_float(name):
            return "{} \\hfill $\\pm {:.0f} \\%$".format(as_2sf(means[name]*1000.0),
                                                   CI95s[name]/ means[name] * 100.0)
            return "{:.1f}".format(means[name]*1000.0)
        
        def format_int(name):
            assert stddevs[name] == 0.0
            return "{:.0f}".format(means[name])



        # Print LATEX
        print(" ".join(full_command))
        print("Times (ms)",)
        print("Total Build SAT", "Solve SAT", "Verify", "Iterations")
        timing_latex.append(
            " & ".join([
                row_name,
                format_float("Total Runtime"),
                format_float("Build SAT"),
                format_float("Solve SAT"),
                format_float("Verify"),
                format_int("Iterations")])
        )
        print(timing_latex[-1])
        print("Total Build SAT", "Solve SAT", "Verify", "Iterations")
        counts_latex.append(
            " & ".join([
                row_name,
                format_int("Valid Solutions"),
                format_int("Unique Solutions"),
                format_int("Iterations"),
                format_int("SAT Variables"),
                format_int("SAT Sln Variables"),
                format_int("SAT Clauses")])
        )
        print(counts_latex[-1])
        print()
    collect_res += str(result['problem']) + "\n"
    collect_res += "Constraints & Total & Build SAT & Solve SAT & Verify & Iterations \\\\ \\hline\n"
    collect_res += " \\\\ \n".join(reversed(timing_latex)) + " \\\\ \\hline\n\n"

    collect_res += str(result['problem']) + "\n"
    collect_res += "Constraints & Valid & Uniq. & Iterations & Var. & Sln Var. & Clauses \\\\ \\hline\n"
    collect_res += " \\\\ \n".join(reversed(counts_latex)) + " \\\\ \\hline\n\n"

print(collect_res)
