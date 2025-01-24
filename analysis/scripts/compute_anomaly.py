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


