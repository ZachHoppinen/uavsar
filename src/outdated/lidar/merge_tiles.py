"""
Tiles QSI Lidar tiles into a complete image.

Usage:
    merge_tiles.py [-i in_dir] [-o out_fp] [-p projected]

Options:
    -i in_dir     Directory containing folders with .adf files to merge
    -o out_fp     Filepath to save image to
    -p projected  Create a tiff in wgs84 as well?
"""

from glob import glob
import os
from os.path import join, exists, basename, dirname
import rasterio
from rasterio.merge import merge
import subprocess
import shlex
from docopt import docopt

def merge_tiles(args):
    output_fp = args.get('-o')
    in_dir = args.get('-i')
    tiff_dir = join(in_dir, 'tiffs')
    os.makedirs(tiff_dir, exist_ok = True)

    wgs84 = args.get('-p')

    l = sorted(glob(join(in_dir, '*/')))
    l = [f for f in l if len(glob(join(f, '*.adf'))) > 0]
    for d in l:
        in_fp = join(d, 'w001001.adf')
        out_fp = join(tiff_dir, basename(d[:-1])+'.tiff')
        if not exists(out_fp):
            cmd = shlex.split(f'gdal_translate -of GTiff {in_fp} {out_fp}')
            subprocess.run(cmd, stdout= subprocess.PIPE)

    src_files_to_mosaic = []
    for tiff in glob(join(tiff_dir, '*.tiff')):
        src = rasterio.open(tiff)
        src_files_to_mosaic.append(src)
    mosaic, out_trans = merge(src_files_to_mosaic)

    output_meta = src.meta.copy()
    output_meta.update(
        {"driver": "GTiff",
            "height": mosaic.shape[1],
            "width": mosaic.shape[2],
            "transform": out_trans,
        }
    )

    with rasterio.open(output_fp, 'w', **output_meta) as m:
        m.write(mosaic)

    if wgs84:
        from rasterio.warp import calculate_default_transform, reproject, Resampling

        dst_crs = 'EPSG:4326'
        with rasterio.open(output_fp) as src:
            transform, width, height = calculate_default_transform(
                src.crs, dst_crs, src.width, src.height, *src.bounds)
            kwargs = src.meta.copy()
            kwargs.update({
                'crs': dst_crs,
                'transform': transform,
                'width': width,
                'height': height
            })

            with rasterio.open(output_fp.replace('.tiff','_wgs84.tiff'), 'w', **kwargs) as dst:
                for i in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(dst, i),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs=dst_crs,
                        resampling=Resampling.nearest)


if __name__ == '__main__':
    args = docopt(__doc__)
    merge_tiles(args)