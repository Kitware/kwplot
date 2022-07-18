import matplotlib as mpl
import IPython
ipython = IPython.get_ipython()
ipython.run_line_magic('matplotlib', 'qt')
backend = 'Qt5Agg'
mpl.use(backend)

from matplotlib import pyplot as plt
import numpy as np

img1 = np.random.rand(128, 128)
img2 = img1.copy()
img2[:, 0:64] = 0

# Showing the initial image works fine.
plt.imshow(img1)

# Should update the previous figure to show a new image
plt.imshow(img2)
