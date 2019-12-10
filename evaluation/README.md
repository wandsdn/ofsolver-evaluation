Scripts used to measure and analyse the results of ofsolver's performance

[measure_ofsolver.py](measure_ofsolver.py): runs ofsolver and collects the results

analyse_* run: Generate latex tables from the results. These scripts require the python library in requirements.txt.

[dump_log.py](dump_log.py): prints the results previously captured by measure_ofsolver.py

[measurements](./measurements) contains the results we collected, from our tests, as captured by measure_ofsolver.py. Note: since running our
measurements we have renamed tools and moved rulesets/pipelines as part of putting
the code and datasets online. We have updated the scripts with the new names.
But the results of our experiments are unmodified and still maintain the
old names.
