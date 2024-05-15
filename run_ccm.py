import numpy as np
import sys
import pandas as pd
import xarray as xr
from pyEDM import *
import argparse
import glob

from scripts.ccm_wrapper import runCCM

########################################################################
# I would recommend making the function a separate script (i.e. treat
# it like a python module that gets imported). This script will then
# call the module and run the analyses. This will make for cleaner code if
# we end up needing to do other analyses in the future. Just a 
# recommendation though, don't feel like you ahve to do it.
########################################################################

# Initialize the ArgumentParser object
parser = argparse.ArgumentParser()

# Add a positional argument
parser.add_argument(
    '-c',
    help='The filename of the climate data to be analyzed.'
)
parser.add_argument(
    '-i', type=int,
    help='The index of the line of latitude to be analyzed.'
)
parser.add_argument(
    '-j', type=int,
    help='The index of the line of longitude to be analyzed.'
)
parser.add_argument(
    '-t',
    help='The index (ntau) of the line of lag (tau) to be analyzed (ntau:tau 0:1, 1:2, 3:6).'
)
parser.add_argument(
    '--verbose',
    dest='verbose',
    default=False,
    action='store_true',
    help='Print i, j, n_tau, and tau to the console?'
)

# Dictionary to convert from ntau to tau values
tau_conversion = {'0':1, '1':3, '2':6}

args = parser.parse_args()

# Being explicit with the test and
if args.verbose == True:
    print(f"climate file: {args.c}")
    print(f"nlat: {args.i}")
    print(f"nlon: {args.j}")
    print(f"ntau: {args.t}")
    print(f"tau: {tau_conversion[args.t]}")

runCCM(args.c, args.i, args.j, int(tau_conversion[args.t]))
