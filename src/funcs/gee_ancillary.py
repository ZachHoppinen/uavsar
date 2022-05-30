## Google Earth Engine section

import os
from os.path import expanduser, join, basename
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, mapping
import rasterio as rio
from rasterio.mask import mask

import ee

# Initialize the Earth Engine module.
ee.Initialize()

# This function computes the feature's geometry area and adds it as a property.
def addArea(feature):
  return feature.set({'areaHa': feature.geometry().area(10).divide(100 * 100)})

def snow_off_phase(img_fp, ann_fp):
    with rio.open(img_fp) as src:
        bounds = src.bounds
        geom = ee.Geometry.BBox(*bounds)
        df = pd.read_csv(ann_fp, index_col = [0])
        s = pd.to_datetime(df.loc['value','start time of acquisition for pass 1']).tz_localize(None)
        e = pd.to_datetime(df.loc['value','start time of acquisition for pass 2']).tz_localize(None)
        try:
            snow_cover = ee.ImageCollection("MODIS/006/MOD10A1").select('NDSI_Snow_Cover').filterDate(s,e).mean().clip(geom)
            vectors = snow_cover.gt(10).reduceToVectors(scale=500).filterMetadata('label','equals',0)
            # Map the area getting function over the FeatureCollection.
            areaAdded = vectors.map(addArea)
            areaAdded = areaAdded.filterMetadata('areaHa','greater_than',10)
            if areaAdded.size().getInfo()>0:
                f = areaAdded.limit(1, 'areaHa', False)
                p = Polygon(f.first().geometry().coordinates().getInfo()[0])
                geoms = [mapping(p)]
                phase_sub, _ = mask(src, geoms, crop=True)
                if np.count_nonzero(~np.isnan(phase_sub)) > 0:
                    snow_off_phase = np.nanmean(phase_sub[0])
                    return snow_off_phase
        except ee.ee_exception.EEException as e:
            print(e)

def atmospheric_h20_diff(img_fp, ann_fp):
    with rio.open(img_fp) as src:
        arr = src.read(1)
        bounds = src.bounds
        geom = ee.Geometry.BBox(*bounds)
        df = pd.read_csv(ann_fp, index_col = [0])
        s = pd.to_datetime(df.loc['value','start time of acquisition for pass 1']).tz_localize(None)
        e = pd.to_datetime(df.loc['value','start time of acquisition for pass 2']).tz_localize(None)
        try:
            atmospheric_h20 = ee.ImageCollection("NCEP_RE/surface_wv").select('pr_wtr').filterDate(s,e)
            atmospheric_f1 = atmospheric_h20.limit(1, 'system:time_start', True).first().reduceRegion(reducer=ee.Reducer.mean(), geometry=geom).get('pr_wtr').getInfo()
            atmospheric_f2 =  atmospheric_h20.limit(1, 'system:time_start', False).first().reduceRegion(reducer=ee.Reducer.mean(), geometry=geom).get('pr_wtr').getInfo()
            h20_diff = atmospheric_f2 - atmospheric_f1
            return h20_diff
        except ee.ee_exception.EEException as e:
            print(e)