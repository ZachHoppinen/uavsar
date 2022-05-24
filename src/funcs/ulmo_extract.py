import os
from os.path import expanduser, join
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
import contextily as ctx
import ulmo
import rasterio as rio
from rasterio.features import dataset_features
from rasterio.windows import Window
import pickle
import pyproj
from shapely.ops import unary_union
from conversion import imperial_to_metric

#This is the latest CUAHSI API endpoint
wsdlurl = 'https://hydroportal.cuahsi.org/Snotel/cuahsi_1_1.asmx?WSDL'
sites_gdf_conus = gpd.read_file('~/scratch/data/uavsar/snotel/ulmo_sites.json')

#Get current datetime
today = datetime.today().strftime('%Y-%m-%d')

def raster_box_extract(img, x_coord, y_coord, box_side = 5):
    meta = img.meta
    # Use the transform in the metadata and your coordinates
    rowcol = rio.transform.rowcol(meta['transform'], xs=x_coord, ys=y_coord)
    w = img.read(1, window=Window(rowcol[1], rowcol[0], box_side, box_side))
    return w

def snotel_fetch(sitecode, start_date='2015-12-01', end_date = '2020-12-01'):
    vals = pd.DataFrame()
    for var in ['SNOTEL:WTEQ_H','SNOTEL:SNWD_H','SNOTEL:TOBS_H']:
        try:
            #Request snowdepths from the server
            values = ulmo.cuahsi.wof.get_values(wsdlurl, sitecode, var, start=start_date, end=end_date)
            #Convert to a Pandas DataFrame   
            values_df = pd.DataFrame.from_dict(values['values'])
            #Parse the datetime values to Pandas Timestamp objects
            values_df['datetime'] = pd.to_datetime(values_df['datetime'], utc=True)
            #Set the DataFrame index to the Timestamps
            values_df = values_df.set_index('datetime')
            #Convert values to float and replace -9999 nodata values with NaN
            values_df['value'] = pd.to_numeric(values_df['value']).replace(-9999, np.nan)
            #Remove any records flagged with lower quality
            values_df = values_df[values_df['quality_control_level_code'] == '1']
            #Rename values
            values_df = values_df.rename(columns = {'value':var})
            values_df = values_df.loc[:, var]
            if vals.size != 0:
                vals = pd.merge(vals, values_df, left_index= True, right_index= True)
            else:
                vals = values_df
        except Exception as e:
            print(e)
            print("Unable to fetch %s" % var)

    return vals

def get_snotel_image_results(img_fp, inc_fp, cor_fp, ann_fp, snotel_gdf = sites_gdf_conus, box_side = 5):
    ann = pd.read_csv(ann_fp)
    with rio.open(img_fp) as src, rio.open(inc_fp) as inc_src, rio.open(cor_fp) as cor_src:
        shapes = list(dataset_features(src, bidx=1, as_mask=False, geographic=True, band=False))
        result = gpd.GeoDataFrame.from_dict(shapes, crs = 'EPSG:4326')
        for i in result.index:
            result.iloc[i]['geometry'] = Polygon(result.iloc[i]['geometry']['coordinates'][0])
        boundary = gpd.GeoSeries(unary_union(result['geometry']))
        boundary_gdf = gpd.GeoDataFrame(boundary, columns = ['geometry'], crs = snotel_gdf.crs)
        points_within = gpd.sjoin(snotel_gdf, boundary_gdf, predicate='within')
        res = {}
        for _, r in points_within.iterrows():
            d = {}
            s = pd.to_datetime(ann.loc[0, 'start time of acquisition for pass 1'])
            e = pd.to_datetime(ann.loc[0, 'start time of acquisition for pass 2'])
            values = snotel_fetch(r['code'], start_date=s, end_date=e)
            # Get units
            if values.size != 0:
                for var in values.columns:
                    unit = ulmo.cuahsi.wof.get_variable_info(wsdlurl, var)['units']['name']
                    d[var] = imperial_to_metric(values.loc[:, var].values ,unit)
                d['phase'] = raster_box_extract(src, r.geometry.x, r.geometry.y, box_side)
                d['inc'] = raster_box_extract(inc_src, r.geometry.x, r.geometry.y, box_side)
                d['cor'] = raster_box_extract(cor_src, r.geometry.x, r.geometry.y, box_side)
                res[r['code']] = d

    return res