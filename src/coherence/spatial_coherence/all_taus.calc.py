
import os
from os.path import join, exists, basename, dirname, expanduser
from glob import glob
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xarray as xr
import rioxarray as rxa
import geopandas as gpd
from scipy.optimize import curve_fit
from rasterio.enums import Resampling
import py3dep

with open(expanduser('~/scratch/data/uavsar/image_fps'), 'rb') as f:
    image_fps = pickle.load(f)

image_fps = [f for f in image_fps if f['fp'].endswith('.unw.grd.tiff')]
netcdf_fps = '/bsuhome/zacharykeskinen/scratch/data/uavsar/images/vv_coherence'

def temp_model(T, tau):
    return np.exp(-T/tau)

def tau(cors, days):
    if np.sum(np.isnan(cors)) == 0:
        s = curve_fit(temp_model, days, cors, 5)[0][0]
        return s
    else:
        return np.nan

for fp in glob(join(netcdf_fps, '*')):
    print(basename(fp))
    with open(fp, 'rb') as f:
        cor_vv = pickle.load(f)
    if len(cor_vv.band.values) > 2:
        days = [int(d.split('_')[-1].replace('d','')) for d in cor_vv.band.values]
        taus = np.apply_along_axis(arr = cor_vv['cor_vv'].values, func1d = tau, axis = 0, days = days)
        da = cor_vv.isel({'band':0})['cor_vv']
        da = da.drop('band')
        da.values = taus
        da.rio.to_raster(join('/bsuhome/zacharykeskinen/uavsar/results/taus', basename(fp).replace('.pkl','.tif')))


