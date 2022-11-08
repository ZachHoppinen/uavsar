from os.path import join, expanduser, basename
from glob import glob
import numpy as np
import xarray as xa
import rioxarray as rxa
import matplotlib.pyplot as plt
import pickle
from tqdm import tqdm
from scipy.optimize import curve_fit

def temp_model(T, tau):
    return np.exp(-T/tau)

def tau(cors, days):
    if np.sum(np.isnan(cors)) == 0:
        s = curve_fit(temp_model, days, cors, 5)[0][0]
        return s
    else:
        return np.nan

# s1ds = glob(join(expanduser('~/scratch/data/uavsar/sentinel/gm'), 'S1*VV*'))
s1ds = glob(join(expanduser('~/scratch/data/uavsar/sentinel/lowman'), 'S1*VV*'))

c1 = rxa.open_rasterio(glob(join(s1ds[0], '*corr.tif'))[0]).rio.reproject('EPSG:4326').rio.clip_box(-108.3, 38.7, -107.9, 39.12)
cor_vv_arr = np.zeros((len(s1ds), *c1.values[0].shape))

for i, fps in tqdm(enumerate(s1ds), total = len(s1ds)):
    c2 = rxa.open_rasterio(glob(join(fps, '*corr.tif'))[0]).rio.reproject_match(c1)
    cor_vv_arr[i] = c2.values[0]

days = [int(d.split('_')[-5].replace('VVP','')) for d in s1ds]

taus = np.apply_along_axis(arr = cor_vv_arr, func1d = tau, axis = 0, days = days)

c1.values[0] = taus

c1.rio.to_raster(join('/bsuhome/zacharykeskinen/uavsar/results/taus','s1_gm.tif'))