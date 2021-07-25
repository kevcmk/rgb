import os
from rgb.display.hzelmatrix import HzelMatrix
from rgb.controlloop import ControlLoop

if __name__ == "__main__":

    matrix_width = int(os.environ.get("MATRIX_WIDTH", 32))
    matrix_height = int(os.environ.get("MATRIX_HEIGHT", 64))
    display = HzelMatrix(dimensions=(matrix_width, matrix_height))
    rgb2d = ControlLoop(display=display)
    rgb2d.initialize_mqtt()
    rgb2d.blocking_loop()