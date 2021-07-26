
from rgb.form.random_shape import RandomIcon
import os
from rgb.utilities import loopwait
from rgb.display.tkcanvas import TkCanvas
from rgb.controlloop import ControlLoop
from rgb.form.iconography import Iconography
from rgb.form.basenoise import *
import time

# if __name__ == "__main__":
#     matrix_width = int(os.environ.get("MATRIX_WIDTH", 32))
#     matrix_height = int(os.environ.get("MATRIX_HEIGHT", 64))
#     display = TkCanvas(dimensions=(matrix_width, matrix_height))
#     rgb2d = ControlLoop(display=display, form=Iconography((matrix_width, matrix_height)))
#     rgb2d.blocking_loop()

hz = 60
max_dt = 1 / hz

events = {
    20: {"type": "note_on", "note": 42, "velocity": 105 },
    30: {"type": "note_on", "note": 43, "velocity": 105 },
    40: {"type": "note_on", "note": 44, "velocity": 105 },
    50: {"type": "note_on", "note": 45, "velocity": 105 },
    90: {"type": "note_off", "note": 45, "velocity": 105 },
    100: {"type": "note_off", "note": 43, "velocity": 105 },
    110: {"type": "note_off", "note": 42, "velocity": 105 },
    120: {"type": "note_off", "note": 44, "velocity": 105 },
}
event_mod = max(events.keys())

if __name__ == "__main__":
    matrix_width = int(os.environ.get("MATRIX_WIDTH", 32))
    matrix_height = int(os.environ.get("MATRIX_HEIGHT", 64))
    display = TkCanvas(dimensions=(matrix_width, matrix_height))
    f = ZNoise((matrix_width, matrix_height))
    i = 0
    t_last = time.time()
    while True:
        i += 1  
        if i % event_mod in events:
            event = events[i % event_mod]
            f.midi_handler(event)
        t_last, total_elapsed_since_last_frame = loopwait(t_last=t_last, max_dt=max_dt)
        step = f.step(total_elapsed_since_last_frame)
        display.display(step)