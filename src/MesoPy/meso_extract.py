"""
Function to capture image bounds and query and return time series of weather observations that overlap non-null values in image.

Usage:
    download-uavsar.py [-c csv_fp] [-o out_dir] [-d debug]

Options:
    -i input_fp   file path to image to extract and bbox
    -c ann_Csv    file path to annotation csv
    -d debug      token for mesowest API ()
"""

import rasterio as rio
from rasterio.windows import Window
import numpy as np
import pandas as pd
from docopt import docopt
from MesoPy import Meso

def raster_box_extract(img, x_coord, y_coord, box_side = 5):
    meta = img.meta

    # Use the transform in the metadata and your coordinates
    rowcol = rio.transform.rowcol(meta['transform'], xs=x_coord, ys=y_coord)

    w = img.read(1, window=Window(rowcol[1], rowcol[0], box_side, box_side))

    return w

def mesopy_date_parse(pd_date_str):
    return pd_date_str.strftime('%Y') + pd_date_str.strftime('%m') + pd_date_str.strftime('%d') + pd_date_str.strftime('%H') + pd_date_str.strftime('%M')

def main(img_fp, start, end, token, anc_img = None):
    token = args.get('-t')
    if not token:
        token = '0191c61bf7914bd49b8bd7a98abb9469'
    img_fp = args.get('-i')
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
        name = float(stat['NAME'].lower().replace(' ',''))
        with rio.open(img_fp) as src:
            w = raster_box_extract(src, long, lat)
        if len(w[~np.isnan(w)]) > 0:
            if name not in stat_ls:
                obs = m.timeseries(start, start, stid = stat['STID'], vars = 'snow_depth')
                if obs:
                    obs = obs['STATION'][0]['OBSERVATIONS']
                    d = {}
                    dt = pd.to_datetime(obs['date_time'])
                    if 'snow_depth_set_1' in obs.keys():
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
                        res[stat['NAME']] = d
            stat_ls.append(name)

    return res

if __name__ == '__main__':
    args = docopt(__doc__)

    main(args)