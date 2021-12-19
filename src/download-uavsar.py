"""
Downloads uavsar images from the Alaska Satellite Facility's Vertex service. The script downloads interferogram, amplitude, coherence, unwrapped phase, and incidence angle of uavsar imgs from the vertex website and converts them to .tiff files.

Usage:
    download-uavsar.py [-c csv_fp] [-o out_dir] [-d debug]

Options:
    -c csv_fp     file path to csv of uavsar vertex download urls
    -o out_dir    directory to save each image into
    -d debug      turns on debugging logging  [default: False]
"""

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
from funcs.file_control import unzip
from funcs.conversion import grd_convert

def main(args):
    run = False

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
    for url in urls.int_url:
        _log.info(f'Starting {url}')
        img_dir = join(out_dir, basename(url).replace('_int_grd.zip',''))
        makedirs(img_dir, exist_ok = True)
        # create temp dir and download interferogram zip file to it
        grd_dir = join(img_dir, 'grd')
        makedirs(grd_dir, exist_ok= True)
        if run:
            downloading(url, grd_dir, user, password)
            # Download amplitude file with same pattern
            downloading(url.replace('INTERFEROMETRY','AMPLITUDE').replace('int','amp'), grd_dir, user, password)
            # Unzip zip file into same directory
            _log.info('Unzipping...')
            unzip(grd_dir, grd_dir, '*.zip')
        # Convert grd files to geographic projection tiffs
        grd_files = glob(join(grd_dir, '*.grd'))
        ann_file = glob(join(grd_dir, '*.ann'))[0]
        grd_convert(grd_files, ann_file, img_dir)

if __name__ == '__main__':
    args = docopt(__doc__)
    _log = log.script(__file__, debug = args.get('-d'))
    main(args)