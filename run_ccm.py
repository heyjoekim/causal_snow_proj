import numpy as np
import sys
import pandas as pd
import xarray as xr
from pyEDM import *


def runCCM(clim, i, j, tau):
    
    df = swe_m_anom.join(sst_m_anom)
    # find embedd dimensions
    d1 = EmbedDimension(dataFrame=df.reset_index(), lib="1 100", pred="201 500", columns='sst')
    d2 = EmbedDimension(dataFrame=df.reset_index(), lib="1 100", pred="201 500", columns='swe_level2')

    ed1 = d1[d1['rho'] == d1['rho'].max()]['E'].item()
    ed2 = d2[d2['rho'] == d2['rho'].max()]['E'].item()

    # run ccm
    result = CCM(dataFrame = df,
                 E=ed1,
                 tau=-1,
                 columns='',
                 target='',
                 libSizes='10 600 20',
                 sample=100,
                 showPlot=False)
    return()
