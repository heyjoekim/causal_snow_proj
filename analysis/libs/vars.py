import numpy as np

# Ecoregions used in originial analysis
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

# MAIN PNW Ecoregion used in analysis
coast_ecos = ['North Cascades',
              'Cascades',
              'Eastern Cascades Slopes and Foothills',
              'Columbia Mountains/Northern Rockies']

# Other ecoregions from eco_regions not used in analysis
ecos_not_in = ['Middle Rockies',
               'Klamath Mountains',
               'Sierra Nevada',
               'Wasatch and Uinta Mountains',
               'Southern Rockies',
               'Idaho Batholith',
               'Canadian Rockies',
               'Blue Mountains',
               'Central Basin and Range',
               'Arizona/New Mexico Mountains',
               'Northern Basin and Range']

# include dirs to write figures
pub_dir_main = './figs/main/'
pub_dir_supp = './figs/supp/'

def mean_abs_error(xx, yy):
    mae = np.mean(np.abs(yy-xx))
    return(mae)
