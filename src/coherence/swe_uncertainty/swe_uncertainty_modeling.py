"""
Trying to recreate figure 26 from Bamler and Hartl (1998)
https://www.researchgate.net/publication/263058382_Synthetic_Aperture_Radar_Interferometry
"""

import numpy as np
from scipy.special import hyp2f1, gamma
from scipy.stats import moment
import matplotlib.pyplot as plt

def coherence_phase(phase_diff, L, coherence, phase = 0):
    """
    Calulate PDF of phase based on coherence and number of looks.
    Equation: 59 from Bamler and Hartl (1998)
    https://www.researchgate.net/publication/263058382_Synthetic_Aperture_Radar_Interferometry
    """
    B = np.abs(coherence) * np.cos(phase_diff -  phase)
    C = (1 - np.abs(coherence)**2)**L
    pdf_phase_diff = gamma(L+1/2)*C*B/(2 * np.sqrt(np.pi) * gamma(L) * (1 - B**2)**(L+1/2)) + C/(2 * np.pi) \
        * hyp2f1(L, 1, 1/2, B**2)
    return pdf_phase_diff

def std_from_pdf(diffs, n, coherence, phase):
    """
    Calculate standard deviation from pdf
    https://math.stackexchange.com/questions/636089/finding-cdf-standard-deviation-and-expected-value-of-a-random-variable
    https://www.texasgateway.org/resource/42-mean-or-expected-value-and-standard-deviation
    https://blogs.ubc.ca/math105/continuous-random-variables/expected-value-variance-standard-deviation/
    """
    phase_pfd = coherence_phase(diffs, n, coherence, phase)
    E_X = np.sum(phase_pfd*diffs)
    var = np.sum((diffs - E_X)**2 * phase_pfd)
    std = np.sqrt(var)
    return std

diffs = np.linspace(-np.pi, np.pi, 100)
for n in [1,2,4,8]:
    phase_pfd = coherence_phase(diffs, n, 0.7, 0)
    plt.plot(diffs, phase_pfd, label = n)
    std = std_from_pdf(diffs, n, 0.7, 0)
    print(str(n)+' - '+str(std))
plt.legend()
plt.ylabel('PDF')
plt.xlabel('$\sigma - \sigma_{0}$')
plt.title('Figure: Probability density function of interferometric phase for different\
 number of looks.')
plt.show()

diffs = np.linspace(-np.pi, np.pi, 100)
cohs = np.linspace(0.01, 0.99, 300)
for n in [1,2,4,8,16]:
    for c in cohs:
            phase_pfd = coherence_phase(diffs, n, c, 0)       
            std = std_from_pdf(diffs, n, c, 0)
            if c == cohs[0]:
                plt.scatter(c, np.rad2deg(std), color = f'C{n}', label = n, s = 1)
            else:
                plt.scatter(c, np.rad2deg(std), color = f'C{n}', s = 1)
plt.xlabel('Coherence')
plt.ylabel('Phase std [deg]')
plt.title('Figure 26: Standard deviation of phase estimate as a function coherence/\
number of independent samples.')
plt.legend()
plt.show()