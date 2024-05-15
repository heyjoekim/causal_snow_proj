import numpy as np
import sys
import pandas as pd
import xarray as xr
from pyEDM import *
import argparse
import glob

########################################################################
# I would recommend making the function a separate script (i.e. treat
# it like a python module that gets imported). This script will then
# call the module and run the analyses. This will make for cleaner code if
# we end up needing to do other analyses in the future. Just a 
# recommendation though, don't feel like you ahve to do it.
########################################################################
def runCCM(clim=args.c, i=args.i, j=args.j, tau=tau_conversion[args.t]):
    # determine which climate variable to 
    if clim == 'SST':
        clim_xr = xr.open_dataset('./data/SST_anoms.nc')
    if clim == 'SLP':
        clim_xr = xr.open_dataset('./data/SLP_anoms.nc')

    # get lag values from tau var
    t_dict = {1:-1, 2:-3, 3:-6}
    tau_val = t_dict.get(tau)

    # get list of swe netcdf files
    swe_files = np.sort(glob.glob('./data/snow_by_eco/*.nc'))
    
    # for saving to CSV or JSON
    lons = []
    lats = []
    ecos = []
    rhos = []
    
    for f in swe_files:

        swe_xr = xr.open_dataset(f)

        # select lat/lon for climate xarray and save as df
        clim_df = clim_xr.isel(lon=i, lat=j).sst.to_dataframe().drop(['lon', 'lat'], axis=1)
        swe_df = swe_xr.swe_level2.mean(dim='sites').to_dataframe()
        df = swe_df.join(clim_df)
        # save variable names
        var1 = df.columns[0]    # usually swe
        var2 = df.columns[1]    # should be SST or SLP
        df = df.dropna()
        df = df.reset_index()

        # FOR JSON:
        lon = float(clim_xr.isel(lon=i).lon.values)
        lat = float(clim_xr.isel(lat=j).lat.values)
        eco = swe_xr.swe_level2.attrs['eco_region']

        df_len = len(df)
        # find embedd dimensions
        d1 = EmbedDimension(dataFrame=df, lib="1 100",
                            pred="201 {}".format(df_len),
                            columns=var2,
                            showPlot=False)
        d2 = EmbedDimension(dataFrame=df, lib="1 100",
                            pred="201 {}".format(df_len),
                            columns=var1,
                            showPlot=False)


        ed1 = d1[d1['rho'] == d1['rho'].max()]['E'].item()
        ed2 = d2[d2['rho'] == d2['rho'].max()]['E'].item()

        # Max libSize must be less than N - (E+1)
        maxN = df_len - (ed2+1)
        # run ccm
        CCMresult = CCM(dataFrame = df,
                     E=int(ed2),
                     tau=-tau_val,
                     columns=var2,
                     target=var1,
                     libSizes='10 {} 20'.format(maxN),
                     sample=100,
                     showPlot=False)
        # if var is anchovy::sst, reads as sst influences anchovy
        # get SST/SLP influence SWE
        rho = CCMresult['{}:{}'.format(var1, var2)].iloc[-1]


        lons.append(lon)
        lats.append(lat)
        ecos.append(eco)
        rhos.append(rho)
    
    # save results
    results = pd.DataFrame({'eco_region': ecos,
                            'lon': lons,
                            'lat': lats,
                            'rho':rhos})

    # We'll need to change this in the future after we figure out the directory
    # structure.
    results.to_csv('./outputs/{}/{}_lon_{}_lat_{}.csv'.format(clim, clim, i, j),
                   index=False)
    return()

# Initialize the ArgumentParser object
parser = argparse.ArgumentParser()

# Add a positional argument
parser.add_argument(
    '-c',
    help='The filename of the climate data to be analyzed.'
)
parser.add_argument(
    '-i',
    help='The index of the line of latitude to be analyzed.'
)
parser.add_argument(
    '-j',
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
tau_conversion = {'0':1, '1':2, '2':6}

# Being explicit with the test and
if args.verbose == True:
    print(f"climate file: {args.c}")
    print(f"nlat: {args.i}")
    print(f"nlon: {args.j}")
    print(f"ntau: {args.t}")
    print(f"tau: {tau_conversion[args.t]}")

runCCM(args.clim, args.i, args.j, args.tau_conversion[args.t])
