import os
from os.path import join, exists, basename, dirname, expanduser
from glob import glob
import numpy as np
import pandas as pd
import pickle
from gee_ancillary import snow_off_phase, atmospheric_h20_diff
from multiprocessing import Pool, cpu_count
from datetime import datetime, date
from rio_geom import rio_to_exterior
import rioxarray as rxa
from metloom.pointdata import CDECPointData, SnotelPointData, MesowestPointData
from metloom.variables import CdecStationVariables, SnotelVariables, MesowestVariables

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

with open(expanduser('~/scratch/data/uavsar/image_fps'), 'rb') as f:
    image_fps = pickle.load(f)

image_fps = [f for f in image_fps if f['fp'].endswith('.unw.grd.tiff')]

tmp_dir = expanduser(f'~/uavsar/results/uavsar_snotel_sd/tmp/')

def process(img_set):
    dic = {}
    desc = pd.read_csv(img_set['ann'], index_col = 0)
    dic['name'] = basename(img_set['fp'])
    dic['first_dt'] = pd.to_datetime(desc.loc['value', 'start time of acquisition for pass 1'])
    dic['second_dt'] = pd.to_datetime(desc.loc['value', 'start time of acquisition for pass 2'])
    dic['diff_dt'] = (dic['second_dt'] - dic['first_dt']).astype('timedelta64[D]')

    dic['pol'] = img_set['pol']
    boundary = rio_to_exterior(img_set['fp'])
    if ', CA' in img_set['fp']:
        ca = True
        vrs = [CdecStationVariables.SWE, CdecStationVariables.SNOWDEPTH, CdecStationVariables.TEMP]
        points = CDECPointData.points_from_geometry(boundary, vrs, snow_courses=False)
    else:
        ca = False
        vrs = [SnotelVariables.SWE, SnotelVariables.SNOWDEPTH, SnotelVariables.TEMP]
        points = SnotelPointData.points_from_geometry(boundary, vrs, snow_courses=False)
    sites = points.to_dataframe()
    sites_results = {}
    for i, site in sites.iterrows():
        site_result = {}
        for label in ['fp','inc','cor','hgt']:
            img = rxa.open_rasterio(img_set[label])
            site_name = site['name']
            if label == 'fp':
                label = 'unw'
            site_result[label] = img.sel(x = site.geometry.x, y = site.geometry.y, method = 'nearest', tolerance = 0.0001).values[0]
        if ca:
            snotel_point = CDECPointData(site.id, "my name")
        else:
            snotel_point = SnotelPointData(site.id, "my name")
        try:
            site_result['meso'] = snotel_point.get_hourly_data(dic['first_dt'], dic['second_dt'], vrs)
        except:
            site_result['meso'] = np.nan
        site_result['geom'] = site.geometry
        sites_results[site_name] = site_result
    dic['snotel_results'] = sites_results
    dic['h20_atmospheric_diff'] = atmospheric_h20_diff(img_fp = img_set['fp'], ann_fp = img_set['ann'])
    with open(join(tmp_dir, basename(img_set['fp'].split('.')[0])), 'wb') as f:
        pickle.dump(dic, f)

start_time = datetime.now()

os.makedirs(tmp_dir, exist_ok= True)

print('Running pooled process')

pool = Pool()                         # Create a multiprocessing Pool
pool.map(process, image_fps)

print('Combining tmp dictionaries.')
res = {}
for f in glob(join(tmp_dir, '*')):
    with open(f, 'rb') as f:
        dic = pickle.load(f)
    res[basename(f)] = dic

with open(expanduser(f'~/uavsar/results/uavsar_snotel_sd/res_df_updated'), 'wb') as f:
    pickle.dump(res, f)

end_time = datetime.now()
print(f'Run Time: {end_time - start_time}')