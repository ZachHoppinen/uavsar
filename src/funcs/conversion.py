import numpy as np

def imperial_to_metric(array, units):
    if type(array) is not np.ndarray:
        array = np.array(array)
    if 'inch' in units.lower():
        return array*0.0254
    if 'feet' in units.lower():
        return array*0.3048
    if 'fahrenheit' in units.lower():
        return (array - 32)/1.8