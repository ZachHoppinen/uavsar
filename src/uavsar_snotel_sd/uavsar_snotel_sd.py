import os
from os.path import join, exists, basename, dirname, expanduser
from glob import glob
import numpy as np
import pandas as pd
import rasterio as rio
from tqdm import tqdm, tqdm_notebook
import matplotlib.pyplot as plt
import pickle
from meso_extract import meso_sd_extract
import multiprocessing

data_dir = '/bsuscratch/zacharykeskinen/data/uavsar/images'

print('Starting snotel sd vs uavsar sd analysis...')
res = pd.DataFrame()

for dir in glob(join(data_dir, '*')):
    pairs = glob(join(dir, '*'))
    pairs = [pair for pair in pairs if basename(pair) != 'tmp']
    for pair in tqdm(pairs, desc = basename(dir)):
        unw_fps = glob(join(pair, '*unw.grd.tiff'))
        for unw_fp in unw_fps:
            dic = {}
            csv_fp = glob(join(pair, '*.csv'))[0]
            inc_fp = glob(join(pair, '*.inc.tiff'))[0]
            desc = pd.read_csv(csv_fp, index_col = 0)
            dic['first_dt'] = pd.to_datetime(desc.loc['value', 'start time of acquisition for pass 1'])
            dic['second_dt'] = pd.to_datetime(desc.loc['value', 'start time of acquisition for pass 2'])
            dic['heading'] = desc.loc['value', 'peg heading']
            dic['pol'] = basename(unw_fp).split('_')[6][4:]
            dic['meso_result'] = meso_sd_extract(img_fp = unw_fp, ann_csv = csv_fp, inc_img = inc_fp, box_side = 5)
            res = pd.concat([res, pd.DataFrame.from_records([dic])])
    with open(expanduser(f'~/uavsar/results/uavsar_snotel_sd/res_df'), 'wb') as f:
        pickle.dump(res, f)

res['diff_dt'] = (res['second_dt'] - res['first_dt']).astype('timedelta64[D]')
with open(expanduser(f'~/uavsar/results/uavsar_snotel_sd/res_df'), 'wb') as f:
    pickle.dump(res, f)