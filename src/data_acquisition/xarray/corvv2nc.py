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
netcdf_fps = '/bsuhome/zacharykeskinen/scratch/data/uavsar/images/vv_coherence'

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

for name in glob(join('/bsuhome/zacharykeskinen/scratch/data/uavsar/images','*,*')):
    site_name = basename(name)
    print("\n")
    print(site_name)
    l_fps = []
    for fps in image_fps:
        if fps['location'] == site_name:
            if fps['pol'] == 'VV':
                l_fps.append(fps)
    if len(l_fps)> 0:
        bands = []
        for i, fps in enumerate(l_fps):
            print(i, end = '.')
            name = basename(fps['fp'])
            name = '_'.join(name.split('.')[0].split('_')[:5])
            bands.append(name)
            cor = rxa.open_rasterio(fps['cor'])
            desc = pd.read_csv(fps['ann'])
            if i == 0:
                # dem = rxa.open_rasterio(fps['hgt'])
                # calculate how to get to 30 metere resolution from 0.0005 degrees
                new_res_m = 30
                y1 = float(desc['grd.row_addr'][0])
                dy = float(desc['grd.row_mult'][0])
                x1 = float(desc['grd.col_addr'][0])
                dx = float(desc['grd.col_mult'][0])
                conversion = (new_res_m/1000) / calc_distance(y1, x1, y1+dy, x1 + dx)
                cor_coarse = cor.rio.reproject(cor.rio.crs, \
                                                shape = (int(cor.rio.height/conversion), int(cor.rio.width/conversion)),
                                                resampling = Resampling.average)
                cor_base = cor_coarse.copy()
                # dem = dem.rio.reproject_match(cor_base)
                cor_coarse.values[0]
                cor_vv = np.zeros((len(l_fps), *cor_coarse.values[0].shape))
            else:
                cor_coarse = cor.rio.reproject_match(cor_base)
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
        cor_vv['x'] = cor_coarse.x
        cor_vv['y'] = cor_coarse.y
        with open(join(netcdf_fps, site_name.replace(' ','_')+'.pkl'), 'wb') as f:
            pickle.dump(cor_vv, f)
        # cor_vv.to_netcdf(join(netcdf_fps, site_name.replace(' ','_')+'.nc'))