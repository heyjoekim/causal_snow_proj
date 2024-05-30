import pandas as pd
import numpy as np
import xarray as xr
import glob

def read_ccm_outputs(clim, t):
    # reads outputs from CCM runs and compiles for clim {SST, SLP}
    # for lags (tau) {1,3,6}.
    # returns one xarray for a clim and t

    # create list of files
    outputs = np.sort(glob.glob('./outputs/{}/*tau_{}.csv'.format(clim, t)))

    # create empty dataframe 
    df = pd.DataFrame()

    # loop to read files in outputs 
    for f in outputs:
        temp_df = pd.read_csv(f)
        
        # concat each output to dataframe, df 
        df = pd.concat([df, temp_df], ignore_index=True)
    
    # convert to xarray
    df_multind = df.set_index(['eco_region', 'lon', 'lat'])
    ccm_array = df_multind.to_xarray()
    return(ccm_array)


def save_ccm(ccm_array, vars, path='./data/processed/'):
    fname_str = 'ccm_{}_tau_{}.nc'.format(vars[0], vars[1])
    ccm_array.to_netcdf(path+fname_str)
    return()
