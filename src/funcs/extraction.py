"""
Command line functions to download and unzip files from url
"""

from os.path import join, basename, exists
from os import makedirs, linesep
import subprocess
from subprocess import PIPE, Popen
from glob import glob
import logging

from . import file_control

def downloading(file, directory, ASF_USER, ASF_PASS):
    _log = logging.getLogger(basename(__file__))

    if exists(join(directory,basename(file))):
        ans = input(f'\nWARNING! You are about overwrite {basename(file)} previously '
                    f'converted UAVSAR Geotiffs files located at {directory}!\nPress Y to'
                    ' continue and any other key to abort: ')

        if ans.lower() == 'y':
            file_control.clear(directory)
            _log.info(f'downloading {file}...')
            process = Popen(['wget',file,f'--user={ASF_USER}',f'--password={ASF_PASS}','-P',directory,'--show-progress','--progress=bar'], stderr=subprocess.PIPE)
        else:
            _log.info('Skipping...')
    else:
        _log.info(f'Downloading {file}...')
        process = Popen(['wget',file,f'--user={ASF_USER}',f'--password={ASF_PASS}','-P',directory,'--show-progress','--progress=bar'], stderr=subprocess.PIPE)