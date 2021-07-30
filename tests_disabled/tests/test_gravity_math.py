import os
import sys

a = [(100.0, 0.0)]
b = [(100.0, 0.0)]

dt = 1 / 2.0
g = -9.8

while a[-1][0] > 0.0:
    new_v = a[-1][1] + dt * g
    new_s = a[-1][0] + new_v * dt
    a.append((new_s, new_v))


while b[-1][0] > 0.0:
    new_v = b[-1][1] + 0.5 * -9.8 * (dt ** 2) # -9.8 m/s^2
    new_s = b[-1][0] + new_v * dt
    b.append((new_s, new_v))

print(list(zip(a,b)))
