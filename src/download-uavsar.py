"""
Downloads uavsar images from the Alaska Satellite Facility's Vertex service.

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
from os.path import join, basename, exists

from funcs import log

def main(args):
    csv_fp = args.get('-c')
    out_dir = args.get(-o)
    _log.debug(f'Inputs: csv - {csv_fp}, out_dir - {out_dir}')
    # Authenticate to ASF server using netrc file or user input
    try:
        (ASF_USER, account, ASF_PASS) = netrc.netrc().authenticators("urs.earthdata.nasa.gov")
    except:
        ASF_USER = input("Enter Username: ")
        ASF_PASS = getpass.getpass("Enter Password: ")

    # Get urls from csv
    urls = pd.read_csv(csv_fp, names = ['int_url'])
    _log.info(f'Found {len(urls)} images in csv...')

    # Loop through urls
    for file in urls.int_url:
        # Check for overwrite
        img_dir = join(out_dir, basename(file))
        if exists(img_dir):
            ans = input(f'\nWARNING! You are about overwrite {basename(file)} \n Press Y to'
                        ' continue and any other key to abort...')
            if ans.lower() == 'y':
                os.makedirs(img_dir, exists_ok = True)
                print(f'Downloading {file}...')
                process = Popen(['wget',file,f'--user={ASF_USER}',f'--password={ASF_PASS}','-P',img_dir,'--progress=bar'], stderr=subprocess.PIPE)
                started = False
                for line in process.stderr:
                    line = line.decode("utf-8", "replace")
                    if started:
                        splited = line.split()
                        if len(splited) == 9:
                            percentage = splited[6]
                            speed = splited[7]
                            remaining = splited[8]
                            print("Downloaded {} with {} per second and {} left.".format(percentage, speed, remaining), end='\r')
                    elif line == os.linesep:
                        started = True
            else:
                print('Skipping...')
        else:
            os.makedirs(img_dir, exists_ok = True)



    # Check if image has already been downloaded

        if exists(join(out_dir,os.path.basename(file))):
        ans = input(f'\nWARNING! You are about overwrite {os.path.basename(file)} previously '
                    f'converted UAVSAR Geotiffs files located at {directory}!\nPress Y to'
                    ' continue and any other key to abort: ')





if __name__ == '__main__':
    _log = log.script(__file__)
    args = docopt(__doc__)
    main(args)