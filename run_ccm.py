import numpy as np
import sys
import pandas as pd
import xarray as xr
from pyEDM import *
import argparse
import json
import glob

def runCCM(clim, i, j, tau):
    # determine which climate variable to 
    if clim == 'SST':
        clim_df = xr.open_dataset('./data/SST_anoms.nc')
    if clim == 'SLP':
        clim_df = xr.open_dataset('./data/SLP_anoms.nc')

    # get lag values from tau var
    t_dict = {1:1, 2:3, 3:6}
    tau_val = t_dict.get(tau)

    swe_df = ''
    clim_df = clim
    df = swe_m_anom.join(sst_m_anom)
    # find embedd dimensions
    d1 = EmbedDimension(dataFrame=df.reset_index(), lib="1 100", pred="201 500", columns='sst')
    d2 = EmbedDimension(dataFrame=df.reset_index(), lib="1 100", pred="201 500", columns='swe_level2')

    ed1 = d1[d1['rho'] == d1['rho'].max()]['E'].item()
    ed2 = d2[d2['rho'] == d2['rho'].max()]['E'].item()

    # run ccm
    result = CCM(dataFrame = df,
                 E=ed1,
                 tau=-1,
                 columns='',
                 target='',
                 libSizes='10 600 20',
                 sample=100,
                 showPlot=False)
    return()

parser = argparse.ArgumentParser(description = 'Python Script to run CCM')
parser.add_argument('clim', choices=['SST','SLP'], help='Climate data filename: SST or SLP')
parser.add_argument('i', type=int, help='Integer i - for lat')
parser.add_argument('j', type=int, help='Integer j - for lon')
parser.add_argument('-t', '--tau', choices=[1,2,3], type=int, help='Lag variable')

args = parser.parse_args()

print('reading clim: {}'.format(args.clim))
print('reading i: {}'.format(args.i))
print('reading j: {}'.format(args.j))
print('reading tau: {}'.format(args.tau))
