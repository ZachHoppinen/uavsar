import rioxarray

fp_to_be_clipped_reprojected = ''
fp_to_match = ''
out_fp = ''

xds = rioxarray.open_rasterio(fp_to_be_clipped_reprojected)
xds_match = rioxarray.open_rasterio(fp_to_match)
xds_repr_match = xds.rio.reproject_match(xds_match)
xds_repr_match.data[0][np.isnan(xds_match.data[0])] = np.nan
xds_repr_match.rio.to_raster(out_fp)

lidar_sd = rxa.open_rasterio(join(data_dir, 'lidar_snow_depth.tiff'))
d = {'lowman_23205_21009_004_210203_L090_CX_01.inc.tiff':'inc.tif','lowman_23205_21008-000_21009-004_0007d_s01_L090VV_01.unw.grd.tiff':'unw.tif', 'lowman_23205_21008-000_21009-004_0007d_s01_L090VV_01.cor.grd.tiff':'cor.tif'}
for fp, out in d.items():
    da = rxa.open_rasterio(join(data_dir, fp))
    da_match = da.rio.reproject_match(lidar_sd)
    da_match.data[0][np.isnan(lidar_sd.data[0])] = np.nan
    da_match.rio.to_raster(join(data_dir, out))