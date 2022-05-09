from glob import glob
import os
from os.path import basename, dirname, join, exists
import pandas as pd
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