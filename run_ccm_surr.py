import numpy as np
import sys
import pandas as pd
import xarray as xr
from pyEDM import *
import argparse
import glob

from scripts.ccm_surrogate import runCCMSurrogate

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
    '-i', type=int,
    help='latitude to be analyzed.'
)
parser.add_argument(
    '-j', type=int,
    help='longitude to be analyzed.'
)
parser.add_argument(
    '-t',
    help='Tau: enter value of lag (positive number)'
)
parser.add_argument(
    '--verbose',
    dest='verbose',
    default=False,
    action='store_true',
    help='Print i, j, n_tau, and tau to the console?'
)

args = parser.parse_args()

# Being explicit with the test and
if args.verbose == True:
    print(f"climate file: {args.c}")
    print(f"nlat: {args.i}")
    print(f"nlon: {args.j}")
    print(f"ntau: {args.t}")

if __name__ == "__main__":
    runCCMSurrogate(args.i, args.j, args.t)
