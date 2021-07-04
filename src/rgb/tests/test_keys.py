from tkinter import *
import os
import sys
import io

import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'rgb')))

import keys

hz = 30
dt = 1/hz
scale = 4
matrix_height = 64
matrix_width = 32
g = keys.Keys((matrix_width, matrix_height))
g.keys[5] = 127
g.keys[2] = 2
img = g.step(dt)
