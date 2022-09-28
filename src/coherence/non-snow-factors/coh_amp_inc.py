import os
from os.path import join, exists, basename, dirname, expanduser
from glob import glob
import shutil
import numpy as np
import pandas as pd
import pickle
from datetime import datetime
from multiprocessing import Pool, cpu_count

import xarray as xa
import rioxarray as rxa
from rioxarray.merge import merge_arrays, merge_datasets

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

with open(expanduser('~/scratch/data/uavsar/image_fps'), 'rb') as f:
    image_fps = pickle.load(f)

image_fps = [f for f in image_fps if f['fp'].endswith('.unw.grd.tiff')]

tmp_dir = expanduser(f'~/uavsar/results/coh_amp_inc/tmp/')
os.makedirs(tmp_dir, exist_ok=True)

def process(img_set):
    res = pd.DataFrame()

    phase = rxa.open_rasterio(img_set['fp'])
    phase.name = 'phase'
    cor = rxa.open_rasterio(img_set['cor'])
    cor.name = 'cor'
    inc = rxa.open_rasterio(img_set['inc'])
    inc.name = 'inc'
    phase = phase.rio.reproject_match(cor)
    inc = inc.rio.reproject_match(cor)
    
    merged = xa.merge([phase,cor,inc])

    N = int(1e6)
    cor_vals = merged.cor.values[0].ravel()
    non_nan = ~np.isnan(cor_vals)
    length = len(cor_vals[non_nan])
    idx = np.random.choice(length, N, replace = False)
    res = pd.DataFrame()
    for name in merged.data_vars:
        res.loc[:,name] = merged[name].values[0].ravel()[non_nan][idx]
    for i,v in img_set.items():
        if i not in ['ann','cor','fp','hgt','inc']:
            res.loc[:,i] = v
    
    with open(join(tmp_dir, basename(img_set['fp'].split('.')[0])), 'wb') as f:
        pickle.dump(res, f)

start_time = datetime.now()

os.makedirs(tmp_dir, exist_ok= True)

print('Running pooled process')
print(f'Using {cpu_count()} cpus.')
# Create a multiprocessing Pool
pool = Pool()
pool.map(process, image_fps)

print('Combining tmp dictionaries.')
super_x = []
for fp in glob(join(tmp_dir, '*')):
    with open(fp, 'rb') as f:
        tmp = pickle.load(f)
    super_x.append(tmp)
res = pd.concat(super_x)

with open(expanduser(f'~/uavsar/results/coh_amp_inc/resv1'), 'wb') as f:
    pickle.dump(res, f)


shutil.rmtree(tmp_dir)

end_time = datetime.now()
print(f'Run Time: {end_time - start_time}')