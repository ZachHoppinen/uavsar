import rioxarray as rxa
import matplotlib.pyplot as plt
cor_vv = rxa.open_rasterio('/bsuhome/zacharykeskinen/scratch/data/uavsar/images/vv_coherence/Salt_Lake_City,_UT.nc')
f, ax= plt.subplots()
cor_vv.sel({'band':'stlake_09127_21008-001_21010-000_0006d'})['cor_vv'].plot(ax = ax)
plt.savefig('/bsuhome/zacharykeskinen/uavsar/figures/nctest.png')