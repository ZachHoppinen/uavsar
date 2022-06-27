import rasterio as rio
from rasterio.features import dataset_features
import geopandas as gpd
from shapely.geometry.polygon import orient
from shapely.geometry import Polygon
from shapely.ops import unary_union

def rio_to_exterior(fp, simplify = False):
    with rio.open(fp) as src:
        shapes = list(dataset_features(src, bidx=1, as_mask=False, geographic=True, band=False))
        result = gpd.GeoDataFrame.from_dict(shapes, crs = 'EPSG:4326')
        for i in result.index:
            result.iloc[i]['geometry'] = Polygon(result.iloc[i]['geometry']['coordinates'][0])
        boundary = gpd.GeoSeries(unary_union(result['geometry']))
        boundary_gdf = gpd.GeoDataFrame(boundary, columns = ['geometry'], crs = 'EPSG:4326')

    if simplify:
        boundary_gdf = orient(boundary_gdf.simplify(0.01, preserve_topology=False).loc[0],sign=1.0)
    return boundary_gdf