import os, shutil, logging
from os import makedirs
from os.path import basename, join, exists
from glob import glob
from zipfile import ZipFile
from tqdm import tqdm

def clear(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def unzip(in_dir, out_dir, suffix):
    _log = logging.getLogger(basename(__file__))
    for file in glob(join(in_dir ,suffix)):
        makedirs(out_dir, exist_ok = True)
        with ZipFile(file, "r") as zip_ref:
            _log.info(f'Extracting {file} to {out_dir}')
            for member in tqdm(zip_ref.infolist(), desc='Extracting '):
                zip_ref.extract(member)