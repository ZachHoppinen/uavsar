"""
Functions from https://github.com/SnowEx/snowexsql by Micah Johnson @micahjohnson150. Used to convert UAVSAR grd and ann files.
"""
import numpy as np
import pandas as pd
import logging
from os.path import basename, join, dirname
import rasterio
from rasterio.crs import CRS
from rasterio.transform import Affine

_log = logging.getLogger(__file__)

def get_encapsulated(str_line, encapsulator):
    """
    Returns items found in the encapsulator, useful for finding units

    Args:
        str_line: String that has encapusulated info we want removed
        encapsulator: string of characters encapusulating info to be removed
    Returns:
        result: list of strings found inside anything between encapsulators

    e.g.
        line = 'density (kg/m^3), temperature (C)'
        ['kg/m^3', 'C'] = get_encapsulated(line, '()')
    """

    result = []

    if len(encapsulator) > 2:
        raise ValueError('encapsulator can only be 1 or 2 chars long!')

    elif len(encapsulator) == 2:
        lcap = encapsulator[0]
        rcap = encapsulator[1]

    else:
        lcap = rcap = encapsulator

    # Split on the lcap
    if lcap in str_line:
        for i, val in enumerate(str_line.split(lcap)):
            # The first one will always be before our encapsulated
            if i != 0:
                if lcap != rcap:
                    result.append(val[0:val.index(rcap)])
                else:
                    result.append(val)

    return result

def read_InSar_annotation(ann_file):
    """
    .ann files describe the INSAR data. Use this function to read all that
    information in and return it as a dictionary

    Expected format:

    `DEM Original Pixel spacing (arcsec) = 1`

    Where this is interpretted as:
    `key (units) = [value]`

    Then stored in the dictionary as:

    `data[key] = {'value':value, 'units':units}`

    values that are found to be numeric and have a decimal are converted to a
    float otherwise numeric data is cast as integers. Everything else is left
    as strings.

    Args:
        ann_file: path to UAVsAR description file
    Returns:
        data: Dictionary containing a dictionary for each entry with keys
              for value, units and comments
    """

    with open(ann_file) as fp:
        lines = fp.readlines()
        fp.close()

    data = {}

    # loop through the data and parse
    for line in lines:

        # Filter out all comments and remove any line returns
        info = line.strip().split(';')
        comment = info[-1].strip().lower()
        info = info[0]

        # ignore empty strings
        if info and "=" in info:
            d = info.split('=')
            name, value = d[0], d[1]

            # Clean up tabs, spaces and line returns
            key = name.split('(')[0].strip().lower()
            units = get_encapsulated(name, '()')
            if not units:
                units = None
            else:
                units = units[0]

            value = value.strip()

            # Cast the values that can be to numbers ###
            if value.strip('-').replace('.', '').isnumeric():
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)

            # Assign each entry as a dictionary with value and units
            data[key] = {'value': value, 'units': units, 'comment': comment}

    # Convert times to datetimes
    for pass_num in ['1', '2']:
        for timing in ['start', 'stop']:
            key = '{} time of acquisition for pass {}'.format(timing, pass_num)
            dt = pd.to_datetime(data[key]['value'])
            dt = dt.astimezone(pytz.timezone('US/Mountain'))
            data[key]['value'] = dt

    return data



def INSAR_to_rasterio(grd_file, desc, out_dir):
    """
    Reads in the UAVSAR interferometry file and saves the real and complex
    value and writes them to GeoTiffs. Requires a .ann file to describe the data.

    Args:
        grd_file: File containing the UAVSAR data
        desc: dictionary of the annotation file.
        out_dir: Directory to output the converted files
    """

    data_map = {'int': 'interferogram',
                'amp1': 'amplitude of pass 1',
                'amp2': 'amplitude of pass 2',
                'cor': 'correlation',
                'unw' : 'unwrapped phase',
                'hgt' : 'dem used in ground projection'} #zk - 9/21 - added unw and hgt to datamap


    # Grab just the filename and make a list splitting it on periods
    fparts = basename(grd_file).split('.')
    fkey = fparts[0]
    ftype = fparts[-2]
    dname = data_map[ftype]
    _log.info('Processing {} file...'.format(dname))

    # Grab the metadata for building our georeference
    nrow = desc['ground range data latitude lines']['value']
    ncol = desc['ground range data longitude samples']['value']

    # Find starting latitude, longitude already at the center
    lat1 = desc['ground range data starting latitude']['value']
    lon1 = desc['ground range data starting longitude']['value']

    # Delta latitude and longitude
    dlat = desc['ground range data latitude spacing']['value']
    dlon = desc['ground range data longitude spacing']['value']
    _log.debug('Expecting data to be shaped {} x {}'.format(nrow, ncol))

    _log.info('Using Deltas for lat/long = {} / {} degrees'.format(dlat, dlon))

    # Read in the data as a tuple representing the real and imaginary
    # components
    _log.info(
        'Reading {} and converting it from binary...'.format(
            basename(grd_file)))

    bytes = desc['{} bytes per pixel'.format(dname.split(' ')[0])]['value']
    _log.info('{} bytes per pixel = {}'.format(dname, bytes))

    # Form the datatypes
    if dname in 'interferogram':
        # Little Endian (<) + real values (float) +  4 bytes (32 bits) = <f4
        dtype = np.dtype([('real', '<f4'), ('imaginary', '<f4')])
    else:
        dtype = np.dtype([('real', '<f{}'.format(bytes))])

    # Read in the data according to the annotation file and bytes
    z = np.fromfile(grd_file, dtype=dtype)

    # Reshape it to match what the text file says the image is
    z = z.reshape(nrow, ncol)

    # Build the transform and CRS
    crs = CRS.from_user_input("EPSG:4326")

    # Lat1/lon1 are already the center so for geotiff were good to go.
    t = Affine.translation(lon1, lat1) * Affine.scale(dlon, dlat)
    ext = out_dir.split('.')[-1]
    fbase = join(
        dirname(out_dir), '.'.join(
            basename(out_dir).split('.')[
                0:-1]) + '.{}.{}')

    for i, comp in enumerate(['real', 'imaginary']):
        if comp in z.dtype.names:
            d = z[comp]
            out = fbase.format(comp, ext)
            _log.info('Writing to {}...'.format(out))
            dataset = rasterio.open(
                out,
                'w+',
                driver='GTiff',
                height=d.shape[0],
                width=d.shape[1],
                count=1,
                dtype=d.dtype,
                crs=crs,
                transform=t,
            )
            # Write out the data
            dataset.write(d, 1)

            # show(new_dataset.read(1), vmax=0.1, vmin=-0.1)
            # for stat in ['min','max','mean','std']:
            #     log.info('{} {} = {}'.format(comp, stat, getattr(d, stat)()))
            dataset.close()