from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt

def f(x, y):
    return np.sin(np.sqrt(x ** 2 + y ** 2))

x = 0
def xx(x, y):
    x = x + 1
    return x

x = np.linspace(-6, 6, 30)
y = np.linspace(-6, 6, 30)

print(x[0])

X, Y = np.meshgrid(x, y)
Z = xx(X, Y)

fig = plt.figure()
ax = plt.axes(projection='3d')
ax.contour3D(X, Y, Z, 50, cmap='binary')
plt.show()