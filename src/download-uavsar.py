"""
Downloads uavsar images from the Alaska Satellite Facility's Vertex service. The script downloads interferogram, amplitude, coherence, unwrapped phase, and incidence angle of uavsar imgs from the vertex website and converts them to .tiff files.

Usage:
    download-uavsar.py [-c csv_fp] [-o out_dir] [-d debug]

Options:
    -c csv_fp     file path to csv of uavsar vertex download urls
    -o out_dir    directory to save each image into
    -d debug      turns on debugging logging  [default: False]
"""

import time
import numpy as np
import pandas as pd
import netrc
import getpass
from docopt import docopt
from glob import glob
from os import makedirs
from os.path import join, basename, exists

from funcs import log
from funcs.extraction import downloading
from funcs.file_control import unzip, clear
from funcs.conversion import grd_convert

def main(args):
    csv_fp = args.get('-c')
    out_dir = args.get('-o')
    assert exists(out_dir) == True, AssertionError('Output directory does not exist.')
    _log.debug(f'Inputs: csv - {csv_fp}, out_dir - {out_dir}')
    # Authenticate to ASF server using netrc file or user input
    try:
        (user, account, password) = netrc.netrc().authenticators("urs.earthdata.nasa.gov")
    except:
        user = input("Enter Username: ")
        password = getpass.getpass("Enter Password: ")

    # Get urls from csv
    urls = pd.read_csv(csv_fp, names = ['int_url'])
    _log.info(f'Found {len(urls)} images...')

    # Loop through urls
    for i, url in enumerate(urls.int_url):
        ans = 'n'
        start = time.perf_counter()

        _log.info(f'Starting {url}. \n {i+1} image of {len(urls)}')
        img_dir = join(out_dir, basename(url).replace('_int_grd.zip',''))
        # create temp dir and download interferogram zip file to it
        if exists(img_dir):
            ans = input(f'\nWARNING! You are about overwrite {basename(img_dir)} located at {out_dir}!.  '
                        f'\nPress Y to continue and any other key to abort: ')

        if ans.lower() == 'y' or exists(img_dir) == False:
            if ans.lower() == 'y':
                clear(img_dir)
            grd_dir = join(img_dir, 'grd')
            makedirs(grd_dir, exist_ok= True)
            downloading(url, grd_dir, user, password)
            # Download amplitude file with same pattern
            downloading(url.replace('INTERFEROMETRY','AMPLITUDE').replace('int','amp'), grd_dir, user, password)
            # Unzip zip file into same directory
            _log.info('Unzipping...')
            unzip(grd_dir, grd_dir, '*.zip')
            # Convert grd files to geographic projection tiffs
            _log.info('Converting...')
            grd_files = glob(join(grd_dir, '*.grd'))
            ann_file = glob(join(grd_dir, '*.ann'))[0]
            grd_convert(grd_files, ann_file, img_dir, debug = debug_op)
            _log.info('Completed! {:0.0f}s elapsed'.format(time.perf_counter() - start))
        else:
            _log.info('Skipping...')

if __name__ == '__main__':
    args = docopt(__doc__)
    debug_op = args.get('-d')
    _log = log.script(__file__, debug = debug_op)
    main(args)