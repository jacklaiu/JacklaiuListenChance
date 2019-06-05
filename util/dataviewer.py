import matplotlib.pyplot as plt
import numpy as np

x = np.arange(1, 11)

fig = plt.figure(1)
ax1 = plt.subplot(2, 1, 1)
ax2 = plt.subplot(2, 1, 2)
l1, = ax1.plot(x, x*x, 'r')
l2, = ax2.plot(x, x*x, 'b')

plt.legend([l1, l2], ['first', 'second'], loc = 'upper right')

plt.show()