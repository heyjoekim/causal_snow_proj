import numpy as np
import sys
import pandas as pd
import xarray as xr
from pyEDM import *
import glob

def runCCM(clim, i, j, tau):
    # determine which climate variable to 
    if clim == 'SST':
        clim_xr = xr.open_dataset('./data/SST_anoms.nc').sst
    if clim == 'SLP':
        clim_xr = xr.open_dataset('./data/SLP_anoms.nc').slp

    # get list of swe netcdf files
    swe_files = np.sort(glob.glob('./data/snow_by_eco/*.nc'))
    
    # for saving to CSV or JSON
    lons = []
    lats = []
    ecos = []
    embedDims = []
    rhos = []
    slopes = []
    rho_rs = []
    
    for f in swe_files:

        swe_xr = xr.open_dataset(f)

        # select lat/lon for climate xarray and save as df
        clim_df = clim_xr.isel(lon=i, lat=j).to_dataframe().drop(['lon', 'lat'], axis=1)
        swe_df = swe_xr.swe_level2.mean(dim='sites').to_dataframe()
        df = swe_df.join(clim_df)
        
        # FOR JSON:
        lon = float(clim_xr.isel(lon=i).lon.values)
        lat = float(clim_xr.isel(lat=j).lat.values)
        eco = swe_xr.swe_level2.attrs['eco_region']

       # check for nan values for masked SST vals
        if clim_df.isnull().any().any():
            lons.append(lon)
            lats.append(lat)
            ecos.append(eco)
            embedDims.append(np.nan)
            rhos.append(np.nan)
            slopes.append(np.nan)
            rho_rs.append(np.nan)
        else:
            # save variable names
            var1 = df.columns[0]    # usually swe
            var2 = df.columns[1]    # should be SST or SLP
            df = df.dropna()
            df = df.reset_index()

            df_len = len(df)

            # convert time to ISO-8601 as required by pyEDM
            df['time'] = df['time'].map(lambda x: x.isoformat())

            # find embeded dimensions
            d1 = EmbedDimension(
                    dataFrame=df,
                    lib=[1, 100],
                    pred=[201, df_len],
                    columns=var2,
                    target=var2,
                    showPlot=False)

            #d2 = EmbedDimension(
            #        dataFrame=df,
            #        lib=[1, 100],
            #        pred=[201, df_len],
            #        columns=var1,
            #        target=var1,
            #        showPlot=False)

            ed1 = d1[d1['rho'] == d1['rho'].max()]['E'].iloc[0]
           #  ed2 = d2[d2['rho'] == d2['rho'].max()]['E'].iloc[0]
            
            # Max libSize must be less than N - (E+1)
            maxN = df_len - (ed1 + 1)
        
            # print(f, ed1, df_len, maxN)
            # run ccm
            CCMresult = CCM(
                    dataFrame = df,
                    E=int(ed1),
                    seed=30,
                    tau=-tau,
                    columns=var2,
                    target=var1,
                    libSizes=[15, maxN-1, 8],
                    sample=100,
                    showPlot=False)

            # if var is anchovy::sst, reads as sst influences anchovy
            # get SST/SLP influence SWE
            rho = CCMresult['{}:{}'.format(var1, var2)].iloc[-1]
            # get SWE influence on SST/SLP
            rho_r = CCMresult['{}:{}'.format(var2, var1)].iloc[-1]
            # calculate the slope to check for convergence
            slope = (CCMresult['{}:{}'.format(var1, var2)].iloc[-1] - CCMresult['{}:{}'.format(var1, var2)].iloc[-20])/(20)


            lons.append(lon)
            lats.append(lat)
            ecos.append(eco)
            embedDims.append(int(ed1))
            rhos.append(np.round(rho,3))
            slopes.append(np.round(slope,3))
            rho_rs.append(np.round(rho_r,3))
    
    # save results
    results = pd.DataFrame({'eco_region': ecos,
                            'lon': lons,
                            'lat': lats,
                            'embed dims': embedDims,
                            'rho': rhos,
                            'slope (last 20)': slopes,
                            'rho reverse': rho_rs})

    # We'll need to change this in the future after we figure out the directory
    # structure.
    results.to_csv('./outputs/{}/{}_lon_{}_lat_{}_tau_{}.csv'.format(clim, clim, i, j, tau),
                   index=False)
    return()
