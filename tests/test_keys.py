from tkinter import *
import os
import sys
import io

import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'rgb')))

from forms import keys

hz = 30
dt = 1/hz
scale = 4
matrix_height = 64
matrix_width = 32
g = keys.Keys((matrix_width, matrix_height))
g.midi_handler({"type": "note_on", "note": 58, "time": 0, "velocity": 127, "channel": 0})
img = g.step(dt)
