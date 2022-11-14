import os
from os.path import join, exists, basename, dirname, expanduser
from glob import glob
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import xarray as xr
import rioxarray as rxa
from scipy import stats

netcdf_fps = '/bsuhome/zacharykeskinen/scratch/data/uavsar/images/vv_coherence'
with open(expanduser('~/scratch/data/uavsar/image_fps'), 'rb') as f:
    image_fps = pickle.load(f)

image_fps = [f for f in image_fps if f['fp'].endswith('.unw.grd.tiff')]

data_fp = '/bsuhome/zacharykeskinen/scratch/data/uavsar/coherence'
with open(join(data_fp,'cor_vv_3.pkl'), 'rb') as f:
    cor_vv = pickle.load(f)

imgs_dir = '/bsuhome/zacharykeskinen/scratch/data/uavsar/images/'
for loc, ds in cor_vv.items():
    for fps in glob(join(imgs_dir, loc.replace('_',' '), '*_grd')):
        band = '_'.join(basename(fps).split('_')[:-5])
        if band not in list(ds.band.values):
            if len(glob(join(fps,'*VV*cor*'))) == 1:
                print(band)
                im = rxa.open_rasterio(glob(join(fps,'*VV*cor*'))[0]).rio.reproject_match(cor_vv[loc])
                new = ds.drop('cor_vv')
                new = new.drop_dims('band')
                new['cor_vv'] = im[0].assign_coords(band = band)
                cor_vv[loc] = xr.concat([cor_vv[loc], new], dim = 'band')
                # cor_vv[loc] = add_band(cor_vv[loc], im, band)
            else:
                print(band)

with open(join(data_fp,'cor_vv_5.pkl'), 'wb') as f:
    pickle.dump(cor_vv, f)