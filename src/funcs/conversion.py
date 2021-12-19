"""
Convert UAVSAR data to geotiffs then reproject to UTM
"""

from tqdm import tqdm
import pandas as pd
from os import listdir, mkdir
from os.path import abspath, basename, dirname, expanduser, isdir, join
import logging
import time

from funcs.snowexsql import read_InSar_annotation, INSAR_to_rasterio

_log = logging.getLogger(__file__)


def grd_convert(grd_files, ann_file, output, epsg, pol = False):
    """
    Convert all grd files from the UAVSAR binary grd to tiff and then saves to the output dir
    Args:
        grd_files: List of *.grd files needed to be converted
        ann_file: .ann file associated with grd files
        output: directory to output files to
        epsg: epsg of the resulting file
    """
    start = time.perf_counter()
    errors = []

    desc = read_InSar_annotation(ann_file)
    # Save annotation data
    base = '_'.join(basename(ann_file).split('_')[0:5])
    desc_out = join(output, (base + '.csv') )
    _log.info('Saving data dict to {}'.format(desc_out))
    desc_dic = pd.DataFrame.from_dict(desc)
    desc_dic.to_csv(desc_out)

    nfiles = len(grd_files)
    if nfiles > 0:
        _log.info('Converting {} UAVSAR .grd files to geotiff...'.format(len(nfiles)))

        for grd_fp in tqdm(sorted(grd_files)):

            # Save to our temporary folder and only change fname to have
            # ext=tif
            latlon_tiff = join(output, basename(grd_fp.replace('grd', 'tif')))
            _log.debug(f'Saving to {latlon_tiff}')
            try:
                # Convert the GRD to a geotiff thats projected in lat long
                INSAR_to_rasterio(grd_fp, desc, latlon_tiff)

            except Exception as e:
                _log.error(e)
                errors.append((grd, e))

        # Report errors an a convenient location for users
        if errors:
            _log.warning(
                '{}/{} files errored out during conversion...'.format(len(errors), nfiles))
            for c in errors:
                f, e = c[0], c[1]
                _log.error('Conversion of {} errored out with:\n{}'.format(f, e))

    _log.info('Completed! {:0.0f}s elapsed'.format(time.perf_counter() - start))