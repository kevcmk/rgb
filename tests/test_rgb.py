import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'rgb')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'rpi-rgb-led-matrix', 'bindings', 'python')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'rpi-rgb-led-matrix', 'bindings', 'python', 'samples')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'rpi-rgb-led-matrix', 'bindings', 'python', 'rgbmatrix')))


print(sys.path)
from rgb import BaseMatrix

@pytest.fixture(scope="function")
def basematrix():
    yield BaseMatrix()

def test_keys(basematrix):
    basematrix.step(1/60)
    basematrix.midi_handler({"type": "note_on", "time": 0, "note": 60, "velocity": 110, "channel": 0})
    basematrix.midi_handler({"type": "note_off", "time": 0, "note": 60, "velocity": 110, "channel": 0})


