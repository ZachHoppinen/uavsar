import metloom
from rio_geom import rio_to_exterior
import rasterio as rio
import pandas as pd
from shapely.geometry import box, Polygon
import pytz
from metloom.pointdata import CDECPointData
from metloom.variables import CdecStationVariables
import geopandas as gpd
from rasterio.features import dataset_features
from shapely.ops import unary_union
from conversion import imperial_to_metric
from rasterio.windows import Window
from ulmo_extract import raster_box_extract

def get_california_snowsites(img_fp, inc_fp, cor_fp, ann_fp, box_side = 5):
    ann = pd.read_csv(ann_fp)
    with rio.open(img_fp) as src, rio.open(inc_fp) as inc_src, rio.open(cor_fp) as cor_src:
        shapes = list(dataset_features(src, bidx=1, as_mask=False, geographic=True, band=False))
        result = gpd.GeoDataFrame.from_dict(shapes)
        for i in result.index:
            result.iloc[i]['geometry'] = Polygon(result.iloc[i]['geometry']['coordinates'][0])
        boundary = gpd.GeoSeries(unary_union(result['geometry']))
        boundary_gdf = gpd.GeoDataFrame(boundary, columns = ['geometry'], crs = 'EPSG:4326')
        vrs = [CdecStationVariables.SWE, CdecStationVariables.SNOWDEPTHß]
        points = CDECPointData.points_from_geometry(boundary_gdf, vrs, snow_courses=False)
        sites = points.to_dataframe()
        res = {}
        for _, r in sites.iterrows():
            cdec_point = CDECPointData(r.id, r.name)
            ann = pd.read_csv(ann_fp)
            s = pd.to_datetime(ann.loc[0, 'start time of acquisition for pass 1'])
            e = pd.to_datetime(ann.loc[0, 'start time of acquisition for pass 2'])
            values = cdec_point.get_daily_data(s, e, variables = vrs)
            if values is not None:
                values = values.dropna(how= 'all', axis = 1)
                d = {}
                idx = [d.date() for d in values.index.levels[0]]
                if s.date() in idx or s.date() + pd.Timedelta('1 day') in idx and e.date() in idx or e.date() - pd.Timedelta('1 day') in idx:
                    for var in vrs:
                        if var.name in values.columns:
                            unit = values[var.name + '_units'].values[0]
                            d[var.name] = imperial_to_metric(array = values[var.name].values, units = unit)
                    d['phase'] = raster_box_extract(src, r.geometry.x, r.geometry.y, box_side)
                    d['inc'] = raster_box_extract(inc_src, r.geometry.x, r.geometry.y, box_side)
                    d['cor'] = raster_box_extract(cor_src, r.geometry.x, r.geometry.y, box_side)
                    res[r['name']] = d
    return res