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

from rasterio.enums import Resampling
import py3dep

with open(expanduser('~/scratch/data/uavsar/image_fps'), 'rb') as f:
    image_fps = pickle.load(f)

image_fps = [f for f in image_fps if f['fp'].endswith('.unw.grd.tiff')]

from math import cos, sin, asin, sqrt, radians
def calc_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km

l_fps = []
for fps in image_fps:
    if fps['location'] == 'Lowman, CO':
        if fps['pol'] == 'VV':
            l_fps.append(fps)

bands = []
for i, fps in enumerate(l_fps):
    print(i, end = '.')
    name = basename(fps['fp'])
    name = '_'.join(name.split('.')[0].split('_')[:5])
    bands.append(name)
    cor = rxa.open_rasterio(fps['cor'])
    desc = pd.read_csv(fps['ann'])
    inc = rxa.open_rasterio(fps['inc'])
    if i == 0:
        # dem = rxa.open_rasterio(fps['hgt'])
        # calculate how to get to 30 metere resolution from 0.0005 degrees
        new_res_m = 30
        y1 = float(desc['grd.row_addr'][0])
        dy = float(desc['grd.row_mult'][0])
        x1 = float(desc['grd.col_addr'][0])
        dx = float(desc['grd.col_mult'][0])
        conversion = (new_res_m/1000) / calc_distance(y1, x1, y1+dy, x1 + dx)
        # conversion = 6
        cor_coarse = cor.rio.reproject(cor.rio.crs, \
                                        shape = (int(cor.rio.height/conversion), int(cor.rio.width/conversion)),
                                        resampling = Resampling.average)
        cor_base = cor_coarse.copy()
        cor_vv = np.zeros((len(l_fps), *cor_coarse.values[0].shape))
        # print(np.nanmax(inc.values[0]))
    else:
        cor_coarse = cor.rio.reproject_match(cor_base)
    inc = inc.rio.reproject_match(cor_base)
    cor_coarse.values[0][inc.values[0] > np.deg2rad(50)] = np.nan
    cor_coarse.values[0][inc.values[0] < np.deg2rad(30)] = np.nan
    cor_vv[i] = cor_coarse.values[0]

cor_vv = xr.Dataset(
    data_vars = dict(
        cor_vv = (["band", "y", "x"], cor_vv)
    ),
    coords = dict(
        lon = (["x"], cor_coarse.x.data),
        lat = (["y"], cor_coarse.y.data),
        band = bands
    ),
    attrs = dict(description = "Coherence for VV over lowman")
)

#cor_vv.sel({'band' : bands[1]})['cor_vv']

cor_coarse.data[0] = cor_vv.reduce(dim = "band", func = np.mean)['cor_vv'].data

cor_coarse.rio.to_raster(os.path.expanduser('~/ave_lowman_high_inc.tiff'), driver = 'COG')