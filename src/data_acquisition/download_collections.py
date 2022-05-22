from glob import glob
import os
from os.path import basename, dirname, join, exists, expanduser
import pickle
import pandas as pd
import numpy as np
import rasterio as rio
from uavsar_pytools import UavsarCollection

data_dir = '/bsuscratch/zacharykeskinen/data/uavsar/images'
collections = ['Grand Mesa, CO','Lowman, CO']
collections = ['Fraser, CO','Ironton, CO', 'Peeler Peak, CO', 'Rocky Mountains NP, CO', 'Silverton, CO', 'Telluride, CO', 'Silver City, ID', 'Reynolds Creek, ID', 'Utica, MT']
collections = ['Salt Lake City, UT','Los Alamos, NM','Eldorado National Forest, CA','Donner Memorial State Park, CA','Sierra National Forest, CA']
for c in collections:
    work_dir = join(data_dir, c)
    os.makedirs(work_dir, exist_ok=True)
    collection = UavsarCollection(collection = c, work_dir = work_dir, clean = True, dates = (pd.to_datetime('20190430'), pd.to_datetime('20220430')), inc = True)
    collection.collection_to_tiffs()

image_fps = []
for loc_dir in glob(join(data_dir, '*')):
    for img_dir in glob(join(loc_dir, '*')):
        if img_dir.endswith('tmp') == False:
            for f in glob(join(img_dir, '*.tiff')):
                csv_fp = glob(join(img_dir, '*.csv'))[0]
                inc_fp = glob(join(img_dir, '*.inc.tiff'))[0]
                d = {}
                d['fp'] = f
                d['ann'] = csv_fp
                d['inc'] = inc_fp
                d['location'] = basename(loc_dir)
                image_fps.append(d)
                with rio.open(f, 'r+') as src:
                    src.nodata = np.nan

with open(expanduser('~/scratch/data/uavsar/image_fps'), 'wb') as f:
    pickle.dump(image_fps, f)