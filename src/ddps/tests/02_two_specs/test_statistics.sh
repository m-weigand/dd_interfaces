#!/bin/bash
test -d results && rm -r results
dd_single.py -f frequencies.dat -d data.dat -n 20 -o results --tausel data_ext\
    --nr_cores=1\
    --tausel data_ext\
    --lambda 1.0\

ddps.py -i results --statistics
