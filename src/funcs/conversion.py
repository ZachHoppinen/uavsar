"""
Convert UAVSAR data to geotiffs then reproject to UTM
"""

import glob
import shutil
from tqdm import tqdm
from os import listdir, mkdir
from os.path import abspath, basename, dirname, expanduser, isdir, join
import logging

from snowexsql.snowexsql.conversions import INSAR_to_rasterio
from snowexsql.snowexsql.metadata import read_InSar_annotation
from snowexsql.snowexsql.projection import reproject_raster_by_epsg
from snowexsql.snowexsql.utilities import read_n_lines

_log = logging.getLogger(basename(__file__))


def grd_convert(grd_files, ann_file, output, epsg, clean_first=False, pol = False):
    """
    Convert all grd files from the UAVSAR binary grd to tiff and then saves to the output dir
    Args:
        grd_files: List of *.grd files needed to be converted
        ann_file: .ann file associated with grd files
        output: directory to output files to
        epsg: epsg of the resulting file
        clean_first: Boolean indicating whether to clear out the output folder first
    """
    desc = read_InSar_annotation(ann)
    # Save annotation data
    base = '_'.join(base_f.split('_')[0:5])
    desc_out = output +'/'+ base +'.csv'
    log.info('Saving data dict to {}'.format(desc_out))
    desc_dic = pd.DataFrame.from_dict(desc)
    desc_dic.to_csv(desc_out)

    nfiles = len(filenames)
    if nfiles > 0:
        log.info('Converting {} UAVSAR .grd files to geotiff...'.format(nfiles))


        for ann in tqdm(sorted(filenames)):
            # open the ann file
            if pol:
                desc = read_PolSar_annotation(ann)
            else:
                desc = read_InSar_annotation(ann)

            # Form a pattern based on the annotation filename
            base_f = basename(ann)
            pattern = '.'.join(base_f.split('.')[0:-1]) + '*.grd'

            #save annotation data
            base = '_'.join(base_f.split('_')[0:5])
            desc_out = output +'/'+ base +'.csv'
            log.info('Saving data dict to {}'.format(desc_out))
            desc_dic = pd.DataFrame.from_dict(desc)
            desc_dic.to_csv(desc_out)

            # Gather all files associated
            grd_files = glob.glob(join(directory, pattern))
            grd_files = set(grd_files)

            log.info(
                'Converting {} grd files to geotiff...'.format(
                    len(grd_files)))

            for grd in grd_files:

                # Save to our temporary folder and only change fname to have
                # ext=tif
                latlon_tiff = grd.replace(directory, temp).replace('grd', 'tif')
                log.debug(f'Saving to {latlon_tiff}')
                try:
                    # Convert the GRD to a geotiff thats projected in lat long
                    INSAR_to_rasterio(grd, desc, latlon_tiff)
                    tiff_pattern = '.'.join(latlon_tiff.split('.')[0:-1]) + '*'
                    tif_files = glob.glob(tiff_pattern)

                    log.info(
                        'Reprojecting {} files to utm...'.format(
                            len(tif_files)))

                    for tif in glob.glob(tiff_pattern):
                        utm_file = tif.replace(temp, output)
                        reproject_raster_by_epsg(tif, utm_file, epsg)
                        completed += 1

                except Exception as e:
                    log.error(e)
                    errors.append((grd, e))

        nfiles = completed + len(errors)
        log.info('Converted {}/{} files.'.format(completed, nfiles))



    # Report errors an a convenient location for users
    if errors:
        log.warning(
            '{}/{} files errored out during conversion...'.format(len(errors), nfiles))
        for c in errors:
            f, e = c[0], c[1]
            log.error('Conversion of {} errored out with:\n{}'.format(f, e))

    # Clean up the temp folder
    log.debug('Removing {}...'.format(temp))
    shutil.rmtree(temp)

    log.info('Completed! {:0.0f}s elapsed'.format(time.time() - start))