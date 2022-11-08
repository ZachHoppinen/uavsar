#!/bin/bash
#SBATCH -J taus # job name
#SBATCH -o /bsuhome/zacharykeskinen/uavsar/logs/%x-%j.log # output and error file name (%j expands to jobID)
#SBATCH -n 1 # total number of tasks requested
#SBATCH -N 1 # number of nodes you want to run on
#SBATCH -p bsudfq # queue (partition)
#SBATCH -t 23:00:00 # run time (hh:mm:ss) - 1 minute in this example.

eval "$(conda shell.bash hook)"
conda activate proj

python /bsuhome/zacharykeskinen/uavsar/src/coherence/spatial_coherence/all_taus.calc.py
