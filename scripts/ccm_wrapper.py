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
    rhos = []
    
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
       
        if clim_df.is_null().any().any():
            lons.append(lon)
            lats.append(lat)
            ecos.append(eco)
            rhos.append(np.round(rho,3))
        else:
            # save variable names
            var1 = df.columns[0]    # usually swe
            var2 = df.columns[1]    # should be SST or SLP
            df = df.dropna()
            df = df.reset_index()


            df_len = len(df)

            # convert time to ISO-8601 as required by pyEDM
            df['time'] = df['time'].map(lambda x: x.isoformat())

            # find embedd dimensions
            d1 = EmbedDimension(
                    dataFrame=df,
                    lib=[1, 100],
                    pred=[201, df_len],
                    columns=var2,
                    target=var2,
                    showPlot=False)

            d2 = EmbedDimension(
                    dataFrame=df,
                    lib=[1, 100],
                    pred=[201, df_len],
                    columns=var1,
                    target=var1,
                    showPlot=False)

            ed1 = d1[d1['rho'] == d1['rho'].max()]['E'].item()
            ed2 = d2[d2['rho'] == d2['rho'].max()]['E'].item()

            # Max libSize must be less than N - (E+1)
            maxN = df_len - (ed1 + 1)
        
            # print(f, ed1, df_len, maxN)
            # run ccm
            CCMresult = CCM(
                    dataFrame = df,
                    E=int(ed1),
                    tau=-tau,
                    columns=var2,
                    target=var1,
                    libSizes=[15, maxN-1, 25],
                    sample=100,
                    showPlot=False)

            # if var is anchovy::sst, reads as sst influences anchovy
            # get SST/SLP influence SWE
            rho = CCMresult['{}:{}'.format(var1, var2)].iloc[-1]


            lons.append(lon)
            lats.append(lat)
            ecos.append(eco)
            rhos.append(np.round(rho,3))
    
    # save results
    results = pd.DataFrame({'eco_region': ecos,
                            'lon': lons,
                            'lat': lats,
                            'rho': rhos})

    # We'll need to change this in the future after we figure out the directory
    # structure.
    results.to_csv('./outputs/{}/{}_lon_{}_lat_{}_tau_{}.csv'.format(clim, clim, i, j, tau),
                   index=False)
    return()
