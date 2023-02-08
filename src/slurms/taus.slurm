#!/bin/bash
#SBATCH -J orbit_compare # orbit_compare
#SBATCH -o /bsuhome/zacharykeskinen/uavsar/logs/%x-%j.log # output and error file name (%j expands to jobID)
#SBATCH -N 1      # nodes requested
#SBATCH -n 1      # tasks requested
#SBATCH -t 24:00:00  # time requested in hour:minute:second

eval "$(conda shell.bash hook)"
conda activate proj

python /bsuhome/zacharykeskinen/uavsar/src/coherence/spatial_coherence/taus/orbit_compare.py
