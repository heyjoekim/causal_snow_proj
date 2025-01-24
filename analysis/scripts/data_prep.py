import io, requests
import xarray as xr
import pandas as pd


# READ AND WRITE ENSO DATA
# This just reads the data from an url
# Sea Surface Temperature (SST) data from http://www.cpc.ncep.noaa.gov/data/indices/
url = 'http://www.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/detrend.nino34.ascii.txt'
s = requests.get(url).content
df = pd.read_csv(io.StringIO(s.decode('utf-8')), delim_whitespace=True)

time_slice = slice('1963-10-01','2019-09-01')

# Parse the time and convert to xarray
time = pd.to_datetime(df.YR.astype(str) + '-' + df.MON.astype(str))
nino34 = xr.DataArray(df.ANOM, dims='time', coords={'time':time})
# Apply a 3-month smoothing window
nino34 = nino34.rolling(time=5, min_periods=3, center=True).mean()
# Select the ERA5 period
nino34 = nino34.sel(time=time_slice)
nino34.to_netcdf('../data/enso/nino34.nc')
# # find periods of El Ninos and La Ninas
# ElNinos = nino34.where(nino34 >= 0.5, drop=True)
# LaNinas = nino34.where(nino34 <= -0.5, drop=True)
