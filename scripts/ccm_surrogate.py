import numpy as np
import sys
import pandas as pd
import xarray as xr
from pyEDM import *
import glob

def runCCMSurrogate(lat, lon, lag):
    # determine which climate variable to 
    clim_xr = xr.open_dataset('./data/SST_anoms.nc').sst

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
    
    for f in swe_files[[3,5,9,10,12,13]]:
        n = 10
        swe_xr = xr.open_dataset(f)

        # select lat/lon for climate xarray and save as df
        clim_df = clim_xr.sel(lon=lon, lat=lat).to_dataframe().drop(['lon', 'lat'], axis=1)
        swe_df = swe_xr.swe_level2.mean(dim='sites').to_dataframe()
        df = swe_df.join(clim_df)
        
        # FOR JSON:
        lon = float(clim_xr.sel(lon=lon).lon.values)
        lat = float(clim_xr.sel(lat=lat).lat.values)
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

            surrogates = SurrogateData(df, column='sst', method='seasonal',
                                       numSurrogates=n)
            surrogates['swe'] = df['swe_level2']
            ccm_surr_by_eco = pd.DataFrame()
            for i in range(n):
                # run ccm
                CCMresult = CCM(
                        dataFrame = surrogates,
                        E=int(ed1),
                        seed=30,
                        tau=-lag,
                        columns='sst_{}'.format(i+1),
                        target='swe',
                        libSizes=[15, maxN-1, 8],
                        sample=100,
                        showPlot=False)
                ccm_surr_by_eco = pd.concat([ccm_surr_by_eco, CCMresult], axis=1)

            ccm_skills = ccm_surr_by_eco[['swe:sst_{}'.format(i+1) for i in range(n)]].mean(axis=1)

            # if var is anchovy::sst, reads as sst influences anchovy
            # get SST influence SWE
            rho = ccm_skills.iloc[-1]
            # get SWE influence on SST/SLP
            #rho_r = CCMresult['{}:{}'.format(var2, var1)].iloc[-1]

            lons.append(lon)
            lats.append(lat)
            ecos.append(eco)
            embedDims.append(int(ed1))
            rhos.append(np.round(rho,3))
            #rho_rs.append(np.round(rho_r,3))
    
    # save results
    results = pd.DataFrame({'eco_region': ecos,
                            'lon': lons,
                            'lat': lats,
                            'embed dims': embedDims,
                            'rho': rhos,
                            'rho reverse': rho_rs})

    # We'll need to change this in the future after we figure out the directory
    # structure.
    results.to_csv('./outputs/surr/surr_lon{}_lat{}_tau{}.csv'.format(lon, lat, lag),
                   index=False)
    return()

#if __name__ == "__main__":
#    runCCMSurrogate(10,200,1)

