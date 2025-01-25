import xarray as xr
import pandas as pd
import geopandas as gpd
import cartopy.crs as ccrs
import numpy as np

# common variables
time_slice = slice('1963-10-01', '2019-09-01')
eco_regions = ['Middle Rockies',
               'Klamath Mountains',
               'Sierra Nevada',
               'Wasatch and Uinta Mountains',
               'Southern Rockies',
               'Idaho Batholith',
               'Columbia Mountains/Northern Rockies',
               'Canadian Rockies',
               'North Cascades',
               'Blue Mountains',
               'Cascades',
               'Eastern Cascades Slopes and Foothills',
               'Central Basin and Range',
               'Arizona/New Mexico Mountains',
               'Northern Basin and Range']

coast_ecos = ['North Cascades',
              'Cascades',
              'Eastern Cascades Slopes and Foothills',
              'Columbia Mountains/Northern Rockies'
              ]


# Compute SST anomalies
f = xr.open_dataset('../../../data/ERSST/sst.mnmean.nc')
ssts = f.sel(time=time_slice)

# select the North Pacific
ssts_np = ssts.sel(lon=slice(180,280), lat=slice(60,-20))
# remove monthly means from North Pacific SSTs
ssta_np = xr.apply_ufunc(
    lambda x, mean: x - mean, 
    ssts_np.sst.groupby('time.month'),
    ssts_np.sst.groupby('time.month').mean(dim='time')
).drop('month')
ssta_np.to_netcdf('../data/SST_anoms.nc')



# SWE anomalies


snotel = xr.open_dataset('../data/snotel/snowPillowSWE_westernNA_level2_ncc.nc')
swe_l1 = xr.open_dataset('../data/snotel/snowPillowSWE_westernNA_level1_ncc.nc')

snotel['agency'] = swe_l1['agency']
# https://stackoverflow.com/a/73073957
snotel['agency'] = snotel.agency.astype('O').sum(dim='agencyName').astype('U')
snotel['siteID'] = snotel.siteID.astype('O').sum(dim='charLenID').astype('U')
snotel['siteName'] = snotel.siteName.astype('O').sum(dim='charLenName').astype('U')

snotel['date_matlab'] = snotel.date_matlab - 679352

snotel.date_matlab.attrs["units"] = "days since 1860-01-01"
snotel = xr.decode_cf(snotel)

swe_da = snotel.swe_level2
lons = snotel.longitude.sel(single=0)
lats = snotel.latitude.sel(single=0)
elev = snotel.elevation.sel(single=0)
time = snotel.date_matlab.transpose('years', 'time', 'sites').stack(xy=['years', 'time']).sel(sites=0).reset_index('xy').reset_coords(names=['years', 'time'], drop=True)

swes = snotel.swe_level2.transpose('years', 'time', 'sites').stack(xy=['years', 'time']).reset_index('xy').reset_coords(names=['years', 'time'], drop=True)
swes = swes.assign_coords({'latitude':lats,
                           'longitude': lons,
                           'elevation':elev,
                           'agency':snotel.agency,
                           'siteID':snotel.siteID,
                           'time': time})
swes = swes.rename({'xy':'time'})
swes = swes.assign_attrs(units='mm')
swes['time'] = swes['time'].to_index()
swes = swes.drop_duplicates(dim='time', keep=False)

swe_mon = swes.resample(time='MS').mean()

delta_swes_mon = xr.apply_ufunc(
    lambda x, mean, stddev: (x - mean)/stddev, 
    swe_mon.groupby('time.month'),
    swe_mon.groupby('time.month').mean(),
    swe_mon.groupby('time.month').std()
).drop('month')
# delta_swes_mon.to_netcdf('./data/processed/SWE_anoms.nc')

# read in NA ECO_LEVEL 3 raster files
gdf = gpd.read_file('../data/NA_CEC_Eco_Level3/')
wus_eco = gdf[gdf['NA_L3NAME'].isin(eco_regions)]

# Define the CartoPy CRS object.
crs = ccrs.PlateCarree()

# This can be converted into a `proj4` string/dict compatible with GeoPandas
crs_proj4 = crs.proj4_init
wus_eco = wus_eco.to_crs(crs_proj4)
# create DataFrame 
test2 = snotel[['agency','siteID','latitude', 'longitude', 'elevation']].to_dataframe()
test2 = test2.droplevel('single')

# convert DataFrame to GeoDataFrame
test_gdf = gpd.GeoDataFrame(test2['agency'],
                            geometry=gpd.points_from_xy(test2['longitude'],
                                                        test2['latitude']))

test_gdf.set_crs(crs_proj4, inplace=True)
test_gdf_w_ecoregions = test_gdf.sjoin(wus_eco, how='inner', predicate='intersects')

def subsetSNOTEL(ecoName): 
    sub = gdf[gdf['NA_L3NAME']==ecoName]
    sub_pc = sub.to_crs(crs_proj4)
    test_gdf_w_ecoregions = test_gdf.sjoin(sub_pc, how='inner', predicate='intersects')
    return(delta_swes_mon.isel(sites=test_gdf_w_ecoregions.index))

for e in eco_regions:
    swe_e = subsetSNOTEL(e)
    e_str = e.replace(' ','_').replace('/','_')
    print('{}; {}; {}; {}; {}; {}'.format(e, 
                                      swe_e.shape[0], 
                                      str(pd.to_datetime(swe_e.mean(dim='sites').dropna(dim='time').time[0].values).date()), 
                                      str(pd.to_datetime(swe_e.mean(dim='sites').dropna(dim='time').time[-1].values).date()),
                                      len(swe_e.mean(dim='sites').dropna(dim='time')),
                                      list(np.unique(swe_e.agency))))
#     swe_e.to_netcdf('../data/processed/snow_by_eco/snow_'+e_str+'.nc')
