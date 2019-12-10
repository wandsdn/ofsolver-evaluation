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
from trepan.api import debug

parser = argparse.ArgumentParser(description='Process results.')
parser.add_argument('infile', type=argparse.FileType('r'), default="DataSets/compression.json")

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

timing_uncompressed = []
timing_compressed = []

plot_total_compressed = []
plot_total_uncompressed = []

timing_latex = []
counts_latex = []
for problem in results["problems"]:
    for combination in problem["combinations"]:
        #debug()
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
            comb_results["Init"].append(
                float(row["Solver Init"]) + float(row["Generating Transformations"]) +
                float(row["Compute Dependencies"]) + float(row["Build SAT Expression"]) +
                float(row["Init SAT Solver"])
                )
            comb_results["Iter"].append(
                float(row["SAT Solving Time"]) - float(row["Init SAT Solver"]) +
                float(row["Solution Building"]) + float(row["Solution Compare"])
                )
            if result["test_options"]:
                is_compressed = False
            else:
                is_compressed = True
            r = re.compile(r".*_(\d*)\.*")
            res = r.search(result["problem"][0])
            hosts_added = res.groups()[0]

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

        def format_datapoint(name):
            """ Format
               (x, y) +- (x err, y err)
            """
            return "({}, {:f}) +- (0, {})".format(hosts_added, means[name]*1000.0, CI95s[name] * 1000.0 )

        def format_int(name):
            assert stddevs[name] == 0.0
            return "{:.0f}".format(means[name])



        # Print LATEX
        #print(" ".join(full_command))
        #print("Times (ms)",)
        #print("Total Build SAT", "Solve SAT", "Verify", "Iterations")
        if is_compressed:
            row = " & ".join([
                    hosts_added,
                    format_float("Total Runtime"),
                    format_float("Pre Solve"),
                    format_float("Init"),
                    format_float("Iter"),
                    format_float("Post Solve"),
                    format_int("Iterations")])
            timing_compressed.append(row)

            plot_total_compressed.append(format_datapoint("Total Runtime")) 
        else:
            row = " & ".join([
                    hosts_added,
                    format_float("Total Runtime"),
                    " --- ",
                    format_float("Init"),
                    format_float("Iter"),
                    " --- ",
                    format_int("Iterations")])
            timing_uncompressed.append(row)
            plot_total_uncompressed.append(format_datapoint("Total Runtime")) 




        #print(timing_latex[-1])
        #print("Total Build SAT", "Solve SAT", "Verify", "Iterations")
        """counts_latex.append(
            " & ".join([
                row_name,
                format_int("Valid Solutions"),
                format_int("Unique Solutions"),
                format_int("Iterations"),
                format_int("SAT Variables"),
                format_int("SAT Sln Variables"),
                format_int("SAT Clauses")])
        )"""
        #print(counts_latex[-1])
        #print()

collect_res += str(result['problem']) + "\n"
collect_res += "!!!!!!!!!!!!! Compressed !!!!!!!!!!!!!!!\n"
collect_res += "Hosts Learnt & Total & Compress & Init & Iter & Apply & Iterations \\\\ \\hline\n"
collect_res += " \\\\ \n".join(timing_compressed) + " \\\\ \\hline\n\n"

collect_res += "\n".join(plot_total_compressed) + "\n\n"

collect_res += "!!!!!!!!!!!! Uncompressed !!!!!!!!!!!!!!!\n"
collect_res += "Hosts Learnt & Total & Compress & Init & Iter & Apply & Iterations \\\\ \\hline\n"
collect_res += " \\\\ \n".join(timing_uncompressed) + " \\\\ \\hline\n\n"

collect_res += "\n".join(plot_total_uncompressed) + "\n\n"


"""
collect_res += str(result['problem']) + "\n"
collect_res += "Constraints & Valid & Uniq. & Iterations & Var. & Sln Var. & Clauses \\\\ \\hline\n"
collect_res += " \\\\ \n".join(reversed(counts_latex)) + " \\\\ \\hline\n\n"
"""



print(collect_res)
