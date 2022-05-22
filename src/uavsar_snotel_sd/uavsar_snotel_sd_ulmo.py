import os
from os.path import join, exists, basename, dirname, expanduser
from glob import glob
import numpy as np
import pandas as pd
import rasterio as rio
from tqdm import tqdm, tqdm_notebook
import matplotlib.pyplot as plt
import pickle
from ulmo_extract import get_snotel_image_results
import multiprocessing
from datetime import datetime

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

print('Starting snotel sd vs uavsar sd analysis...')
res = pd.DataFrame()

with open(expanduser('~/scratch/data/uavsar/image_fps'), 'rb') as f:
    image_fps = pickle.load(f)

image_fps = [f for f in image_fps if f['fp'].endswith('.unw.grd.tiff')]

def process(img, res):
    dic = {}
    desc = pd.read_csv(img['ann'], index_col = 0)
    dic['first_dt'] = pd.to_datetime(desc.loc['value', 'start time of acquisition for pass 1'])
    dic['second_dt'] = pd.to_datetime(desc.loc['value', 'start time of acquisition for pass 2'])
    dic['pol'] = basename(img['fp']).split('_')[6][4:]
    dic['result'] = get_snotel_image_results(img['fp'], img['inc'], img['ann'])
    res = pd.concat([res, pd.DataFrame.from_records([dic])])
    with open(expanduser(f'~/uavsar/results/uavsar_snotel_sd/res_df'), 'wb') as f:
        pickle.dump(res, f)
    return res

loc_old = None
start_time = datetime.now()
for img in image_fps:
    loc_new = img['location']
    if loc_new != loc_old:
        print(f'Starting {loc_new}')
    res = process(img, res)
    print(res.shape)
    loc_old = loc_new

res['diff_dt'] = (res['second_dt'] - res['first_dt']).astype('timedelta64[D]')
with open(expanduser(f'~/uavsar/results/uavsar_snotel_sd/res_df'), 'wb') as f:
    pickle.dump(res, f)

end_time = datetime.now()
print(f'Run Time: {end_time - start_time}')