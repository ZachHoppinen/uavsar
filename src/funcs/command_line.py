"""
Command line functions to download and unzip files from url
"""

from os.path import join, basename, exists
from os import makedirs, linesep
import subprocess
from subprocess import PIPE, Popen
from glob import glob
from zipfile import ZipFile
from . import log

def downloading(file, directory, ASF_USER, ASF_PASS, _log):
    if exists(join(directory,basename(file))):
        ans = input(f'\nWARNING! You are about overwrite {os.path.basename(file)} previously '
                    f'converted UAVSAR Geotiffs files located at {directory}!\nPress Y to'
                    ' continue and any other key to abort: ')

        if ans.lower() == 'y':
            _log.info(f'downloading {file}...')
            process = Popen(['wget',file,f'--user={ASF_USER}',f'--password={ASF_PASS}','-P',directory,'--progress=bar'], stderr=subprocess.PIPE)
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
            _log.info('Skipping...')
    else:
        _log.info(f'Downloading {file}...')
        process = Popen(['wget',file,f'--user={ASF_USER}',f'--password={ASF_PASS}','-P',directory,'--progress=bar'], stderr=subprocess.PIPE)
        started = False
        for line in process.stderr:
            line = line.decode("utf-8", "replace")
            if started:
                splited = line.split()
                if len(splited) == 9:
                    percentage = splited[6]
                    speed = splited[7]
                    remaining = splited[8]
                    _log.info("Downloaded {} with {} per second and {} left.".format(percentage, speed, remaining), end='\r')
            elif line == linesep:
                started = True
            else:
                _log.warning(line)


def unzip(in_dir, out_dir, suffix):
    for file in glob(join(in_dir ,suffix)):
        if not exists(out_dir):
            makedirs(out_dir, exist_ok = True)
            with ZipFile(file, "r") as zip_ref:
                _log.info(f'Extracting {file} to {out_dir}')
                zip_ref.extractall(out_dir)
                _log.info("done")