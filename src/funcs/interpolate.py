from scipy import interpolate
import numpy as np

def grid_interpolate(array):
    x = np.arange(0, array.shape[1])
    y = np.arange(0, array.shape[0])
    #mask invalid values
    array = np.ma.masked_invalid(array)
    xx, yy = np.meshgrid(x, y)
    #get only the valid values
    x1 = xx[~array.mask]
    y1 = yy[~array.mask]
    newarr = array[~array.mask]

    return interpolate.griddata((x1, y1), newarr.ravel(),
                            (xx, yy), method='cubic')