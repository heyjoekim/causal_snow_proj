#!/bin/bash

# comment out line for snwo with eco_regions
singularity exec -H ~/causal_snow_proj ~/causal_snow_proj/container/causal_snow_proj.sif python ~/causal_snow_proj/run_ccm_surr.py -i $1 -j $2 -t $3
