from uavsar_pytools import UavsarScene
from uavsar_pytools.polsar import H_A_alpha_decomp
import os

data_dir = os.path.expanduser('~/scratch/')

url1= 'https://uavsar.asf.alaska.edu/UA_lowman_23205_21015_008_210303_L090_CX_01/lowman_23205_21015_008_210303_L090_CX_01_grd.zip'
url2 = 'https://uavsar.asf.alaska.edu/UA_lowman_23205_21017_018_210310_L090_CX_01/lowman_23205_21017_018_210310_L090_CX_01_grd.zip'
url3 = 'https://uavsar.asf.alaska.edu/UA_lowman_05208_21017_019_210310_L090_CX_01/lowman_05208_21017_019_210310_L090_CX_01_grd.zip'
url4 = 'https://uavsar.asf.alaska.edu/UA_lowman_05208_21015_009_210303_L090_CX_01/lowman_05208_21015_009_210303_L090_CX_01_grd.zip'
for url in [url1, url2,url3, url4]:
    s = UavsarScene(work_dir=data_dir, url = url)
    s.url_to_tiffs()

dir1 = os.path.expanduser(os.path.join(data_dir, 'lowman_05208_21015_009_210303_L090_CX_01_grd'))
dir2 = os.path.expanduser(os.path.join(data_dir, 'lowman_05208_21017_019_210310_L090_CX_01_grd'))
dir3= os.path.expanduser(os.path.join(data_dir, 'lowman_23205_21015_008_210303_L090_CX_01_grd'))
dir4 = os.path.expanduser(os.path.join(data_dir, 'lowman_23205_21017_018_210310_L090_CX_01_grd'))

for dir in [dir1,dir2,dir3,dir4]:
    H_A_alpha_decomp(dir, dir)