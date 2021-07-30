import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from rgb.form.keys import Keys
from rgb.form.randomobject import *
from rgb.form.orbit import *
from rgb.utilities import loopwait

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
    30: {"type": "note_on", "note": 43, "velocity": 105 },
    35: {"type": "control_change", "time": 0, "control": 64, "value": 127, "channel": 0}, # Sustain
    40: {"type": "note_on", "note": 44, "velocity": 105 },
    45: None,
    50: {"type": "note_on", "note": 45, "velocity": 105 },
    # Release Sustain
    55: {"type": "control_change", "time": 0, "control": 64, "value": 0, "channel": 0}, # Release Sustain

    90: {"type": "note_off", "note": 42, "velocity": 105 },
    100: {"type": "note_off", "note": 43, "velocity": 105 },
    110: {"type": "note_off", "note": 44, "velocity": 105 },
    115: None,
    120: {"type": "note_off", "note": 45, "velocity": 105 },
    130: None,
    
}
event_mod = max(events.keys())
sorted_events = sorted(events.keys())

matrix_width = int(os.environ.get("MATRIX_WIDTH", 32))
matrix_height = int(os.environ.get("MATRIX_HEIGHT", 64))

def drive_event_loop_through_form(f: BaseForm):
    for _ in range(2):
        for i, event in enumerate(sorted_events):
            dt = sorted_events[i] - sorted_events[i-1] if i > 0 else sorted_events[i]
            if events[event] is not None:
                f.midi_handler(events[event])
            f.step(dt)

@pytest.mark.parametrize("form", [RandomOutlineCircle, RandomOutlineShape, RandomSolidShape, RandomWord, RandomJapaneseWord, RandomNumber, RandomIcon])
def test_randomobject(form):
    f = form((matrix_width, matrix_height))
    drive_event_loop_through_form(f)

@pytest.mark.parametrize("form", [Orbit])
def test_orbit(form):
    f = form((matrix_width, matrix_height), fast_forward_scale=1.0)
    drive_event_loop_through_form(f)

@pytest.mark.parametrize("form", [Keys])
def test_keys(form):
    f = form((matrix_width, matrix_height))
    drive_event_loop_through_form(f)

@pytest.mark.parametrize("form", [Gravity, GravityKeys, GravityKeysMultiNozzle])
def test_gravity(form):
    f = form((matrix_width, matrix_height), meters_per_pixel=0.006)
    drive_event_loop_through_form(f)
