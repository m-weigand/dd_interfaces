#!/usr/bin/python
import numpy as np
from NDimInv.plot_helper import *
import NDimInv.colecole as colecole
import shutil
shutil
frequencies = np.logspace(-2, 4, 20)

fin = np.hstack((frequencies, frequencies))

# generate Cole-Cole parameters
data = []
rho0 = 8e6
for nr, m in enumerate(np.linspace(0.9, 1, 4)):
    cc_pars = [np.log(rho0), m, np.log(0.04), 0.8]

    # generate CR response
    magpha = colecole.cole_log(fin, cc_pars)
    magpha[0, :] = np.exp(magpha[0, :])
    data.append(magpha.flatten())

data = np.array(data)

# save files
np.savetxt('frequencies.dat', frequencies)
np.savetxt('data.dat', data)
