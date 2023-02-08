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

with open(expanduser('~/scratch/data/uavsar/image_fps'), 'rb') as f:
    image_fps = pickle.load(f)

image_fps = [f for f in image_fps if f['fp'].endswith('.unw.grd.tiff')]
netcdf_fps = '/bsuhome/zacharykeskinen/scratch/data/uavsar/images/vv_coherence'

for fp in glob(join(netcdf_fps, '*')):
    with open(fp, 'rb') as f:
        cor_vv = pickle.load(f)

from scipy.optimize import curve_fit

def fit_coh_decay_model(cohs, days, tau_guess, bounds, xtol, ftol, gamma_inf_guess = 0.3):
    # https://rowannicholls.github.io/python/curve_fitting/exponential.html

    # Fit the function a * np.exp(b * t) + c to x and y
    params, pcov = curve_fit(lambda t, gamma_inf, tau: gamma_inf + (1 - gamma_inf) * np.exp(- t / tau), x, y, p0=(gamma_inf_guess, tau_guess),\
        bounds = bounds, ftol = ftol, xtol = xtol)

    gamma_inf, tau = params

    return gamma_inf, tau, pcov

print('Running full.')

for fp in glob(join(netcdf_fps, '*Lowman*')):
    with open(fp, 'rb') as f:
        cor_vv = pickle.load(f)

days = [int(d.split('_')[-1].replace('d','')) for d in cor_vv.band.values]
taus = np.apply_along_axis(arr = cor_vv['cor_vv'].values, func1d = fit_coh_decay_model, axis = 0, days = days, tau_guess = 30,\
    bounds = ([0, 0], [1, 600]), ftol = 1, xtol = 1)

with open('/bsuhome/zacharykeskinen/uavsar/results/orbit_compare/lowman_full.pkl', 'wb') as f:
    pickle.dump(taus, f)

days = [int(d.split('_')[-1].replace('d','')) for d in cor_vv.band.values]
taus = np.apply_along_axis(arr = cor_vv['cor_vv'].values, func1d = fit_coh_decay_model, axis = 0, days = days, tau_guess = 30,\
    bounds = ([0, 0], [1, 600]), ftol = 1, xtol = 1)

with open('/bsuhome/zacharykeskinen/uavsar/results/orbit_compare/lowman_full.pkl', 'wb') as f:
    pickle.dump(taus, f)

orbits = {'05208': [], '23205': []}
for b in cor_vv.band.values:
    if '05208' in b:
        orbits['05208'].append(b)
    if '23205' in b:
        orbits['23205'].append(b)

for k, v in orbits.items():
    print(f'Running {k}')
    sub = cor_vv.sel(band = v)
    days = [int(d.split('_')[-1].replace('d','')) for d in sub.band.values]
    taus = np.apply_along_axis(arr = sub['cor_vv'].values, func1d = fit_coh_decay_model, axis = 0, days = days, tau_guess = 30,\
        bounds = ([0, 0], [1, 600]), ftol = 1, xtol = 1)
    
    with open(f'/bsuhome/zacharykeskinen/uavsar/results/orbit_compare/{k}.pkl', 'wb') as f:
        pickle.dump(taus, f)



