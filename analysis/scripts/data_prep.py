import os, io, requests
import xarray as xr
import pandas as pd
import cdsapi


current_dir = os.getcwd()
# READ AND WRITE ENSO DATA
# This just reads the data from an url
# Sea Surface Temperature (SST) data from http://www.cpc.ncep.noaa.gov/data/indices/
print('READING: ENSO NINO3.4 INDEX')
url = 'http://www.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/detrend.nino34.ascii.txt'
s = requests.get(url).content
df = pd.read_csv(io.StringIO(s.decode('utf-8')), sep='\s+')

time_slice = slice('1963-10-01','2019-09-01')

# Parse the time and convert to xarray
time = pd.to_datetime(df.YR.astype(str) + '-' + df.MON.astype(str))
nino34 = xr.DataArray(df.ANOM, dims='time', coords={'time':time})
# Apply a 3-month smoothing window
nino34 = nino34.rolling(time=5, min_periods=3, center=True).mean()
# Select the ERA5 period
nino34 = nino34.sel(time=time_slice)
print("WRITING TO analysis/data/enso/")
#nino34.to_netcdf('../data/enso/nino34.nc')
print("FINISHED ENSO")

print('')
print('DOWNLOADING ERA5 DATA')
dataset = "reanalysis-era5-single-levels-monthly-means"
request = {
    "product_type": ["monthly_averaged_reanalysis"],
    "variable": ["mean_sea_level_pressure"],
    "year":[
        "1940", "1941", "1942",
        "1943", "1944", "1945",
        "1946", "1947", "1948",
        "1949", "1950", "1951",
        "1952", "1953", "1954",
        "1955", "1956", "1957",
        "1958", "1959", "1960",
        "1961", "1962", "1963",
        "1964", "1965", "1966",
        "1967", "1968", "1969",
        "1970", "1971", "1972",
        "1973", "1974", "1975",
        "1976", "1977", "1978",
        "1979", "1980", "1981",
        "1982", "1983", "1984",
        "1985", "1986", "1987",
        "1988", "1989", "1990",
        "1991", "1992", "1993",
        "1994", "1995", "1996",
        "1997", "1998", "1999",
        "2000", "2001", "2002",
        "2003", "2004", "2005",
        "2006", "2007", "2008",
        "2009", "2010", "2011",
        "2012", "2013", "2014",
        "2015", "2016", "2017",
        "2018", "2019"],
    "month": [
        '01', '02', '03', '04', '05', '06',
        '07', '08', '09', '10', '11', '12'],
    "time": ["00:00"],
    "data_format": "netcdf",
    "download_format": "unarchived",
    "area": [60, 120, -20, 280]
}

print("WRITING TO analysis/data/ERA/")
os.chdir('../data/ERA/')
target = 'ERA5_mslp_pacific.nc'
client = cdsapi.Client()
client.retrieve(dataset, request, target)
print("FINISHED ERA")

os.chdir(current_dir)
