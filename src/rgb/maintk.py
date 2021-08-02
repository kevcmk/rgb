from rgb.form.keys import Keys
from rgb.form.sustainobject import *
import os
from rgb.utilities import loopwait
from rgb.display.tkcanvas import TkCanvas
from rgb.controlloop import ControlLoop
from rgb.form.iconography import Iconography
from rgb.form.keys import Keys
from rgb.form.basenoise import *
from rgb.form.cells import *
from rgb.form.gravity import *
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
    30: {"type": "note_on", "note": 45, "velocity": 105 },
    # Sustain note 44 and 45
    35: {"type": "control_change", "time": 0, "control": 64, "value": 127, "channel": 0},
    40: {"type": "note_on", "note": 48, "velocity": 105 },
    50: {"type": "note_on", "note": 51, "velocity": 105 },
    90: {"type": "note_off", "note": 42, "velocity": 105 },
    100: {"type": "note_off", "note": 45, "velocity": 105 },
    110: {"type": "note_off", "note": 51, "velocity": 105 },
    120: {"type": "note_off", "note": 48, "velocity": 105 },
    # Release note 44 and 45
    180: {"type": "control_change", "time": 0, "control": 64, "value": 0, "channel": 0}
}
event_mod = max(events.keys())

if __name__ == "__main__":
    matrix_width = int(os.environ.get("MATRIX_WIDTH", 32))
    matrix_height = int(os.environ.get("MATRIX_HEIGHT", 64))
    display = TkCanvas(dimensions=(matrix_width, matrix_height))
    f = VerticalKeys((matrix_width, matrix_height))
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