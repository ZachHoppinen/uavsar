import os
from os.path import join, exists, basename, dirname, expanduser
from glob import glob
import numpy as np
import pandas as pd
import pickle
from ulmo_extract import get_snotel_image_results
from multiprocessing import Pool, cpu_count
from datetime import datetime

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

print('Starting snotel sd vs uavsar sd analysis...')
print(f'Creating {cpu_count()}-process pool')
res = pd.DataFrame()

with open(expanduser('~/scratch/data/uavsar/image_fps'), 'rb') as f:
    image_fps = pickle.load(f)

image_fps = [f for f in image_fps if f['fp'].endswith('.unw.grd.tiff')]
image_fps = iter(image_fps)

tmp_dir = expanduser(f'~/uavsar/results/uavsar_snotel_sd/tmp/')

def process(img):
    dic = {}
    desc = pd.read_csv(img['ann'], index_col = 0)
    dic['name'] = basename(img['fp'])
    dic['first_dt'] = pd.to_datetime(desc.loc['value', 'start time of acquisition for pass 1']) #pd.todateime will need to be removed before next run. already done before pickling
    dic['second_dt'] = pd.to_datetime(desc.loc['value', 'start time of acquisition for pass 2'])
    dic['pol'] = basename(img['fp']).split('_')[6][4:] # in img['pol'] now
    dic['result'] = get_snotel_image_results(img['fp'], img['inc'], img['ann'])
    # res = pd.concat([res, pd.DataFrame.from_records([dic])])
    with open(join(tmp_dir, basename(img['fp'])), 'wb') as f:
        pickle.dump(dic, f)

# loc_old = None
start_time = datetime.now()

os.makedirs(tmp_dir, exist_ok= True)

pool = Pool()                         # Create a multiprocessing Pool
pool.map(process, image_fps)

res = pd.DataFrame()
for f in glob(join(tmp_dir, '*')):
    with open(f, 'rb') as f:
        dic = pickle.load(f)
    res = pd.concat([res, pd.DataFrame.from_records([dic])])

res['diff_dt'] = (res['second_dt'] - res['first_dt']).astype('timedelta64[D]')
with open(expanduser(f'~/uavsar/results/uavsar_snotel_sd/res_df'), 'wb') as f:
    pickle.dump(res, f)

end_time = datetime.now()
print(f'Run Time: {end_time - start_time}')