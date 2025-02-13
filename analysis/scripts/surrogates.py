import numpy as np
import pandas as pd
import xarray as xr
import glob

#from libs.vars import *
from pyEDM import *

time_slice = slice('1963-10-01', '2019-09-01')
nino34 = xr.open_dataset('../data/enso/nino34.nc')

pdo = xr.open_dataset('../data/PDO/pdo.timeseries.ersstv5.nc')
pdo = pdo.sel(time=time_slice)

swe_by_eco_paths = glob.glob('../data/snow_by_eco/*.nc')

def CCMsetup(i, col):
    swe_anoms_by_eco = xr.open_dataset(swe_by_eco_paths[i])
    swe_anoms_ts = swe_anoms_by_eco.mean(dim='sites').dropna(dim='time')
    
    # generate predicted SWE from SST
    swe = swe_anoms_ts.to_dataframe()
    #sst = goa_sst.mean(dim=['lat','lon']).to_dataframe()
    col = col.to_dataframe()
    #swe_by_eco_files[i]

    df = swe.join(col)
    df = df.dropna()
    df = df.reset_index()
    # df = df.drop(['lat', 'lon'], axis=1)
    
    df['time'] = df['time'].map(lambda x: x.isoformat())
    return(df)

def embedDimWrapper(df, var):
    L = len(df)
    d = EmbedDimension(
            dataFrame=df,
            lib=[1,100],
            pred=[201, L],
            columns=[var],
            target=var, showPlot=False)
    return(d[d['rho'] == d['rho'].max()]['E'].iloc[0])

if __name__ == "__main__":
    ecos = []
    lags = []
    skills = []

    for idx, eco in zip([-1, 5, 8, 10], ['Cascades', 'Eastern Cascades Slopes and Foothills', 'North Cascades', 'Columbia Mountains/Northern Rockies']):
        df = CCMsetup(idx, nino34)
        E = embedDimWrapper(df, 'ANOM')
        L = len(df)
        maxN = L-(E+1)
        df = df[['time', 'ANOM', 'swe_level2']]

        s = 50
        surrogates = SurrogateData(df, column='ANOM', method='seasonal', numSurrogates=s)
        surrogates['swe'] = df['swe_level2']

        ccm_surr = pd.DataFrame()
        for l in [-1, -3, -6]:
            for i in range(s):
                test = CCM(dataFrame=surrogates,
                           E = int(E),
                           seed=30,
                           tau=l,
                           target=['ANOM_{}'.format(i+1)],
                           columns='swe',
                           libSizes=[15,maxN-1,8],
                           sample=100)
                ccm_surr = pd.concat([ccm_surr, test], axis=1)

            surr_skill = ccm_surr[['swe:ANOM_{}'.format(i+1) for i in range(s)]].mean(axis=1)
            ecos.append(eco)
            lags.append(np.abs(l))
            skills.append(surr_skill.iloc[-1])
    
    nino_surr_vals = pd.DataFrame({
        'ecoregion':ecos,
        'lags': lags,
        'skill': skills
        })

    nino_surr_vals.to_csv('./enso_surrogates.csv',
                          index=False)
