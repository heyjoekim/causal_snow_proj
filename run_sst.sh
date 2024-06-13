#!/bin/bash

# comment out line for snwo with eco_regions
singularity exec -H ~/causal_snow_proj ~/causal_snow_proj/container/causal_snow_proj.sif python ~/causal_snow_proj/run_ccm.py -c $1 -i $2 -j $3 -t $4

# comment out line for snow for entire western United States
singularity exec -H ~/causal_snow_proj ~/causal_snow_proj/container/causal_snow_proj.sif python ~/causal_snow_proj/run_ccm_wus.py -c $1 -i $2 -j $3 -t $4
