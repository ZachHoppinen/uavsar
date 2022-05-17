def find_roots(x):
    roots = []
    for i in range(1, int(x/2)):
        if x%i == 0:
            roots.append(i)
    return roots

import numpy as np
from os.path import expanduser

for _ in range(10):
    a = np.random.randint(1000000)
    roots = find_roots(a)
    s = f'Found {len(roots)} roots for {a}!\n'
    print(s)

    with open(expanduser('~/uavsar/src/play/root.txt'), 'a') as f:
        f.write(s)