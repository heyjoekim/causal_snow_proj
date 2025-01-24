import xarray as xr
import numpy as np

time_slice = slice('1963-10-01', '2019-09-01')

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
