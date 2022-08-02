import os
from os.path import join, exists, basename, dirname, expanduser
from glob import glob
import numpy as np
import pandas as pd
import rasterio as rio
from tqdm import tqdm, tqdm_notebook
import matplotlib.pyplot as plt
import pickle
from meso_extract import meso_notebook_extract

data_dir = '/bsuscratch/zacharykeskinen/data/uavsar/images'


# # Temporal Baseline Analysis

res = pd.DataFrame()
print('Starting temporal baseline vs coherence analysis...')
for dir in glob(join(data_dir, '*')):
    pairs = glob(join(dir, '*'))
    pairs = [pair for pair in pairs if basename(pair) != 'tmp']
    for pair in tqdm(pairs, desc = basename(dir)):
        coh_fps = glob(join(pair, '*cor.grd.tiff'))
        for coh_fp in coh_fps:
            dic = {}
            desc = pd.read_csv(glob(join(pair, '*.csv'))[0], index_col = 0)
            dic['first_dt'] = pd.to_datetime(desc.loc['value', 'start time of acquisition for pass 1'])
            dic['second_dt'] = pd.to_datetime(desc.loc['value', 'start time of acquisition for pass 2'])
            dic['heading'] = desc.loc['value', 'peg heading']
            dic['pol'] = basename(coh_fp).split('_')[6][4:]
            dic['location'] = basename(dir)
            with rio.open(coh_fp) as src:
                arr = src.read(1)
                dic['coh_25'], dic['coh_75'] = np.nanquantile(arr, [0.25, 0.75])
                dic['median_coh'] = np.nanmedian(arr)
            res = pd.concat([res, pd.DataFrame.from_records([dic])])
res['diff_dt'] = (res['second_dt'] - res['first_dt']).astype('timedelta64[D]')
with open(expanduser('~/uavsar/results/time_coh/res_df_full'), 'wb') as f:
    pickle.dump(res, f)

# # Snotel Values

# print('Starting snow depth difference vs coherence analysis...')
# res = pd.DataFrame()

# for dir in glob(join(data_dir, '*')):
#     pairs = glob(join(dir, '*'))
#     pairs = [pair for pair in pairs if basename(pair) != 'tmp']
#     for pair in tqdm(pairs, desc = basename(dir)):
#         coh_fps = glob(join(pair, '*cor.grd.tiff'))
#         for coh_fp in coh_fps:
#             dic = {}
#             csv_fp = glob(join(pair, '*.csv'))[0]
#             desc = pd.read_csv(csv_fp, index_col = 0)
#             dic['first_dt'] = pd.to_datetime(desc.loc['value', 'start time of acquisition for pass 1'])
#             dic['second_dt'] = pd.to_datetime(desc.loc['value', 'start time of acquisition for pass 2'])
#             dic['heading'] = desc.loc['value', 'peg heading']
#             dic['pol'] = basename(coh_fp).split('_')[6][4:]
#             dic['meso_result'] = meso_notebook_extract(img_fp=coh_fp, ann_csv = csv_fp, col_in = 'snow_depth_set_1', box_side=10)
#             res = pd.concat([res, pd.DataFrame.from_records([dic])])
# res['diff_dt'] = (res['second_dt'] - res['first_dt']).astype('timedelta64[D]')
# with open(expanduser(f'~/uavsar/results/coherence/coh_snotel_sd/res_df_full'), 'wb') as f:
#     pickle.dump(res, f)


# print('Starting mean temperature vs coherence analysis...')
# res = pd.DataFrame()

# for dir in glob(join(data_dir, '*')):
#     pairs = glob(join(dir, '*'))
#     pairs = [pair for pair in pairs if basename(pair) != 'tmp']
#     for pair in tqdm(pairs, desc = basename(dir)):
#         coh_fps = glob(join(pair, '*cor.grd.tiff'))
#         for coh_fp in coh_fps:
#             dic = {}
#             csv_fp = glob(join(pair, '*.csv'))[0]
#             desc = pd.read_csv(csv_fp, index_col = 0)
#             dic['first_dt'] = pd.to_datetime(desc.loc['value', 'start time of acquisition for pass 1'])
#             dic['second_dt'] = pd.to_datetime(desc.loc['value', 'start time of acquisition for pass 2'])
#             dic['heading'] = desc.loc['value', 'peg heading']
#             dic['pol'] = basename(coh_fp).split('_')[6][4:]
#             dic['meso_result'] = meso_notebook_extract(method = 'mean' ,img_fp=coh_fp, ann_csv = csv_fp, col_in = 'air_temp_set_1', box_side=10)
#             res = pd.concat([res, pd.DataFrame.from_records([dic])])
# res['diff_dt'] = (res['second_dt'] - res['first_dt']).astype('timedelta64[D]')
# with open(expanduser(f'~/uavsar/results/coherence/coh_snotel_temp/res_df_mean'), 'wb') as f:
#     pickle.dump(res, f)

# print('Starting melting degree day vs coherence analysis...')
# res = pd.DataFrame()

# for dir in glob(join(data_dir, '*')):
#     pairs = glob(join(dir, '*'))
#     pairs = [pair for pair in pairs if basename(pair) != 'tmp']
#     for pair in tqdm(pairs, desc = basename(dir)):
#         coh_fps = glob(join(pair, '*cor.grd.tiff'))
#         for coh_fp in coh_fps:
#             dic = {}
#             csv_fp = glob(join(pair, '*.csv'))[0]
#             desc = pd.read_csv(csv_fp, index_col = 0)
#             dic['first_dt'] = pd.to_datetime(desc.loc['value', 'start time of acquisition for pass 1'])
#             dic['second_dt'] = pd.to_datetime(desc.loc['value', 'start time of acquisition for pass 2'])
#             dic['heading'] = desc.loc['value', 'peg heading']
#             dic['pol'] = basename(coh_fp).split('_')[6][4:]
#             dic['meso_result'] = meso_notebook_extract(method = 'dmd' ,img_fp=coh_fp, ann_csv = csv_fp, col_in = 'air_temp_set_1', box_side=10)
#             res = pd.concat([res, pd.DataFrame.from_records([dic])])
# res['diff_dt'] = (res['second_dt'] - res['first_dt']).astype('timedelta64[D]')
# with open(expanduser(f'~/uavsar/results/coherence/coh_snotel_temp/res_df_dmd'), 'wb') as f:
#     pickle.dump(res, f)

# print('Starting temperature difference vs coherence analysis...')
# res = pd.DataFrame()

# for dir in glob(join(data_dir, '*')):
#     pairs = glob(join(dir, '*'))
#     pairs = [pair for pair in pairs if basename(pair) != 'tmp']
#     for pair in tqdm(pairs, desc = basename(dir)):
#         coh_fps = glob(join(pair, '*cor.grd.tiff'))
#         for coh_fp in coh_fps:
#             dic = {}
#             csv_fp = glob(join(pair, '*.csv'))[0]
#             desc = pd.read_csv(csv_fp, index_col = 0)
#             dic['first_dt'] = pd.to_datetime(desc.loc['value', 'start time of acquisition for pass 1'])
#             dic['second_dt'] = pd.to_datetime(desc.loc['value', 'start time of acquisition for pass 2'])
#             dic['heading'] = desc.loc['value', 'peg heading']
#             dic['pol'] = basename(coh_fp).split('_')[6][4:]
#             dic['meso_result'] = meso_notebook_extract(method = 'diff' ,img_fp=coh_fp, ann_csv = csv_fp, col_in = 'air_temp_set_1', box_side=10)
#             res = pd.concat([res, pd.DataFrame.from_records([dic])])
# res['diff_dt'] = (res['second_dt'] - res['first_dt']).astype('timedelta64[D]')
# with open(expanduser(f'~/uavsar/results/coherence/coh_snotel_temp/res_df_diff'), 'wb') as f:
#     pickle.dump(res, f)

# print('Starting sd and temp vs coherence analysis...')
# res = pd.DataFrame()

# for dir in glob(join(data_dir, '*')):
#     pairs = glob(join(dir, '*'))
#     pairs = [pair for pair in pairs if basename(pair) != 'tmp']
#     for pair in tqdm(pairs, desc = basename(dir)):
#         coh_fps = glob(join(pair, '*cor.grd.tiff'))
#         for coh_fp in coh_fps:
#             dic = {}
#             csv_fp = glob(join(pair, '*.csv'))[0]
#             desc = pd.read_csv(csv_fp, index_col = 0)
#             dic['first_dt'] = pd.to_datetime(desc.loc['value', 'start time of acquisition for pass 1'])
#             dic['second_dt'] = pd.to_datetime(desc.loc['value', 'start time of acquisition for pass 2'])
#             dic['heading'] = desc.loc['value', 'peg heading']
#             dic['pol'] = basename(coh_fp).split('_')[6][4:]
#             dic['meso_result'] = meso_notebook_extract(method = 'full' ,img_fp=coh_fp, ann_csv = csv_fp, box_side=5)
#             res = pd.concat([res, pd.DataFrame.from_records([dic])])
#     with open(expanduser(f'~/uavsar/results/coherence/coh_snotel_full/res_df'), 'wb') as f:
#         pickle.dump(res, f)

# res['diff_dt'] = (res['second_dt'] - res['first_dt']).astype('timedelta64[D]')
# with open(expanduser(f'~/uavsar/results/coherence/coh_snotel_full/res_df'), 'wb') as f:
#     pickle.dump(res, f)