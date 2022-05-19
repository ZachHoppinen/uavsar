"""
Function to capture image bounds and query and return time series of weather observations that overlap non-null values in image.

Usage:
    meso_extract.py [-i input_fp] [-c ann_csv] [-o out_fp] [-t token]

Options:
    -i input_fp   file path to image to extract and bbox
    -c ann_csv    file path to annotation csv
    -o out_fp     file path to save dictionary
    -t token      token for mesowest API ()
"""

from distutils.command.sdist import sdist
import rasterio as rio
from rasterio.windows import Window
import numpy as np
import pandas as pd
from docopt import docopt
from MesoPy import Meso
from os.path import join
import pickle

def raster_box_extract(img, x_coord, y_coord, box_side = 5):
    meta = img.meta

    # Use the transform in the metadata and your coordinates
    rowcol = rio.transform.rowcol(meta['transform'], xs=x_coord, ys=y_coord)

    w = img.read(1, window=Window(rowcol[1], rowcol[0], box_side, box_side))

    return w

def mesopy_date_parse(pd_date_str):
    return pd_date_str.strftime('%Y') + pd_date_str.strftime('%m') + pd_date_str.strftime('%d') + pd_date_str.strftime('%H') + pd_date_str.strftime('%M')

def main(args, anc_img = None):
    token = args.get('-t')
    if not token:
        token = '0191c61bf7914bd49b8bd7a98abb9469'
    img_fp = args.get('-i')
    out_fp = args.get('-o')
    ann_df = pd.read_csv(args.get('-c'))

    start = pd.to_datetime(ann_df['stop time of acquisition for pass 1'][0])
    end = pd.to_datetime(ann_df['start time of acquisition for pass 2'][0])
    start = mesopy_date_parse(start)
    end = mesopy_date_parse(end)


    m = Meso(token=token)
    with rio.open(img_fp) as src:
        bounds  = src.bounds
    stat_ls = []
    res = {}

    for stat in m.metadata(start = start, end = end, bbox = bounds)['STATION']:
        long = float(stat['LONGITUDE'])
        lat = float(stat['LATITUDE'])
        name = stat['NAME'].lower().replace(' ','')
        with rio.open(img_fp) as src:
            w = raster_box_extract(src, long, lat)
        if len(w[~np.isnan(w)]) > 0:
            if name not in stat_ls:

                obs = m.timeseries(start, end, stid = stat['STID'], vars = 'snow_depth')
                if obs:
                    obs = obs['STATION'][0]['OBSERVATIONS']
                    d = {}
                    dt = pd.to_datetime(obs['date_time'])
                    if 'snow_depth_set_1' in obs.keys():
                        stat_ls.append(name)
                        d['datetime'] = dt
                        d['img_arr'] = w

                        if anc_img:
                            with rio.open(img_fp) as src_anc:
                                w_anc = raster_box_extract(src_anc, long, lat)
                                d['anc_img'] = w_anc

                        d['snow_depth_set_1'] = obs['snow_depth_set_1']
                        for anc_col in ['air_temp_set_1','snow_water_equiv_set_1']:
                            if anc_col in obs.keys():
                                d[anc_col] = obs[anc_col]

                        d['elev'] = stat['ELEVATION']
                        d['lat'] = stat['LATITUDE']
                        d['long'] = stat['LONGITUDE']
                        d['tz'] = stat['TIMEZONE']
                        d['img_fp'] = img_fp
                        res[stat['NAME']] = d
    if res:
        with open(out_fp, 'wb') as f:
            pickle.dump(res, f)
    else:
        print('No results found...')

if __name__ == '__main__':
    args = docopt(__doc__)

    main(args)

## python meso_extract.py -i /home/zacharykeskinen/uavsar/data/slc_stack/lowman_23205_20002-007_20007-003_0013d_s01_L090_01_int_grd/lowman_23205_20002-007_20007-003_0013d_s01_L090VV_01.cor.grd.tiff -c /home/zacharykeskinen/uavsar/data/slc_stack/lowman_23205_20002-007_20007-003_0013d_s01_L090_01_int_grd/lowman_23205_20002-007_20007-003_0013d_s01_L090_01_int_grd.csv -o ~/uavsar/results/test_wx.csv


def meso_notebook_extract(img_fp, ann_csv, col_in = 'snow_depth_set_1', method = 'diff',anc_img = None, token = None, box_side = 10):
    """
    Function for use in notebooks to capture image bounds and query and return time series of weather observations that overlap non-null values in image.
    Params:
    img_fp - filepath to tiff file to extract from
    ann_csv - filepath to annotation csv
    col_in - column of interest. Good options include: 'snow_depth_set_1', 'air_temp_set_1', 'snow_water_equiv_set_1'
    anc_img - anncilary image to also extract values from at same locations as original
    token - Mesopy token (optional). Can be obtained at http://mesowest.org/api/signup/.
    method - difference last and first day? Mean over period? Degree Melting Days?
    """
    if not token:
        token = '0191c61bf7914bd49b8bd7a98abb9469'
    ann_df = pd.read_csv(ann_csv)

    start = pd.to_datetime(ann_df['stop time of acquisition for pass 1'][0])
    end = pd.to_datetime(ann_df['start time of acquisition for pass 2'][0])
    start = mesopy_date_parse(start)
    end = mesopy_date_parse(end)
    m = Meso(token=token)
    with rio.open(img_fp) as src:
        bounds  = src.bounds
    stat_ls = []
    res = {}
    if method != 'full':
        col_name = col_in.replace('_set_1', '')

        for stat in m.metadata(start = start, end = end, bbox = bounds)['STATION']:
            long = float(stat['LONGITUDE'])
            lat = float(stat['LATITUDE'])
            name = stat['NAME'].lower().replace(' ','')
            with rio.open(img_fp) as src:
                w = raster_box_extract(src, long, lat, box_side = box_side)
            if len(w[~np.isnan(w)]) > 0:
                if name not in stat_ls:
                    obs = m.timeseries(start, end, stid = stat['STID'], vars = col_name, units = 'height|m')
                    if obs:
                        unit = obs['UNITS'][col_name]
                        obs = obs['STATION'][0]['OBSERVATIONS']
                        d = {}
                        dt = pd.to_datetime(obs['date_time'])
                        values = obs[col_in]
                        values = [elem for elem in values if elem is not None]
                        if col_in in obs.keys():
                            stat_ls.append(name)
                            if method == 'diff':
                                df = pd.DataFrame(obs[col_in], index = dt)
                                df = df.resample('D').mean()
                                delta = (df.iloc[-1] - df.iloc[0]).values[0]
                                if unit == 'Millimeters':
                                    delta /= 1000
                                elif unit == 'Centimeters':
                                    delta /= 100
                                d[f'delta_{col_name}'] = delta
                            elif method == 'mean':
                                mean = np.nanmean(values)
                                if unit == 'Millimeters':
                                    mean /= 1000
                                elif unit == 'Centimeters':
                                    mean /= 10
                                d[f'mean_{col_name}'] = mean
                            elif method == 'dmd':
                                df = pd.DataFrame(obs[col_in], index = dt)
                                df = df.resample('D').mean()
                                df = df[(df[0].notnull()) & (df[0]>0)]
                                dmd_sum = np.nansum(df)
                                d[f'degmeltday_{col_name}'] = dmd_sum

                            d['img_arr_mean'] = np.nanmean(w)

                            if anc_img:
                                with rio.open(img_fp) as src_anc:
                                    w_anc = raster_box_extract(src_anc, long, lat, box_side = box_side)
                                    d['anc_img'] = np.nanmean(w_anc)

                            d['elev'] = stat['ELEVATION']
                            d['lat'] = stat['LATITUDE']
                            d['long'] = stat['LONGITUDE']
                            d['tz'] = stat['TIMEZONE']
                            d['img_fp'] = img_fp
                            res[stat['NAME']] = d

    else:
        for stat in m.metadata(start = start, end = end, bbox = bounds)['STATION']:
            long = float(stat['LONGITUDE'])
            lat = float(stat['LATITUDE'])
            name = stat['NAME'].lower().replace(' ','')
            with rio.open(img_fp) as src:
                w = raster_box_extract(src, long, lat, box_side = box_side)
                img_mean = np.nanmean(src.read(1))

            if len(w[~np.isnan(w)]) > 0:
                if name not in stat_ls:
                    obs = m.timeseries(start, end, stid = stat['STID'], vars = ['snow_depth','air_temp'], units = 'height|m')
                    if obs and 'snow_depth' in obs['UNITS'].keys() and 'air_temp' in obs['UNITS'].keys():
                        m_unit = obs['UNITS']['snow_depth']
                        obs = obs['STATION'][0]['OBSERVATIONS']
                        d = {}
                        dt = pd.to_datetime(obs['date_time'])
                        sds = obs['snow_depth_set_1']
                        sds = [elem for elem in sds if elem is not None]
                        temp = obs['air_temp_set_1']
                        temp = [elem for elem in temp if elem is not None]
                        stat_ls.append(name)
                        df = pd.DataFrame(obs['snow_depth_set_1'], index = dt)
                        df = df.resample('D').mean()
                        if df.iloc[-1].values[0] > 0.1:
                            delta = (df.iloc[-1] - df.iloc[0]).values[0]
                            if m_unit == 'Millimeters':
                                delta /= 1000
                            elif m_unit == 'Centimeters':
                                delta /= 100
                            d[f'delta_sd'] = delta

                            mean_t = np.nanmean(temp)
                            d[f'mean_temp'] = mean_t

                            df = pd.DataFrame(obs['air_temp_set_1'], index = dt)
                            df = df.resample('D').mean()
                            df = df[(df[0].notnull()) & (df[0]>0)]
                            dmd_sum = np.nansum(df)
                            d[f'degmeltday'] = dmd_sum

                            d['snotel_coh_mean'] = np.nanmean(w)

                            if anc_img:
                                with rio.open(img_fp) as src_anc:
                                    w_anc = raster_box_extract(src_anc, long, lat, box_side = box_side)
                                    d['anc_img'] = np.nanmean(w_anc)

                            d['elev'] = stat['ELEVATION']
                            d['lat'] = stat['LATITUDE']
                            d['long'] = stat['LONGITUDE']
                            d['tz'] = stat['TIMEZONE']
                            d['img_fp'] = img_fp
                            d['img_coh_mean'] = img_mean
                            res[stat['NAME']] = d

    if res:
        return res
    else:
        print('No results found...')

