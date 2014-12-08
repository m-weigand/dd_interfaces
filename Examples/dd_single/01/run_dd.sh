#!/bin/bash
# use the resistivity model for the Debye decomposition
test -d results && rm -r results
dd_single.py -f frequencies.dat -d data.dat -n 20 -o results --nr_cores=1\
     --plot --plot_lcurve -1

# use the conductivity model for the Debye decomposition
# notice that the conductivity model should always be normed to 10 S/m
test -d results_cond && rm -r results_cond
DD_COND=1 dd_single.py -f frequencies.dat -d data.dat\
    -n 20\
    -o results_cond\
    --nr_cores=1\
    --plot\
    --plot_lcurve -1\
    --norm 10
