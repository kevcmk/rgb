import os
from rgb.display.tkcanvas import TkCanvas
from rgb.controlloop import ControlLoop
from rgb.form.iconography import Iconography

if __name__ == "__main__":
    matrix_width = int(os.environ.get("MATRIX_WIDTH", 32))
    matrix_height = int(os.environ.get("MATRIX_HEIGHT", 64))
    display = TkCanvas(dimensions=(matrix_width, matrix_height))
    rgb2d = ControlLoop(display=display, form=Iconography((matrix_width, matrix_height)))
    rgb2d.blocking_loop()
