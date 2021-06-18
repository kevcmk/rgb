
import colorsys
import logging
import os
import time

import numpy as np
import numpy.typing as npt
from samplebase import SampleBase

import gravity

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))

class BaseMatrix(SampleBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser.add_argument("-f", "--form", action="store", help="Extra Kevin argument. The form of LED to take.")
        self.parser.add_argument("--max-fps", action="store", help="Maximum frame rate")

    def run(self):
        
        if self.args.form == "gravity":
            self.form = gravity.Gravity(64, 32, 0.320, 0.160, 60, 1)
        else:
            raise ValueError(f"Unrecognized form: {self.parser.form}")

        hz = int(self.args.max_fps)
        dt = 1 / hz # Seconds
        log.info(f"Running gravity at {hz} Hz...")
        offset_canvas = self.matrix.CreateFrameCanvas()
        i = 0
        
        t_start = time.time()
        t_last = t_start
        
        while True:
            
            a = time.time()
            matrix = self.form.step(dt)
            b = time.time()
            # for i,j,_ in np.ndindex(matrix.shape):
            #     offset_canvas.SetPixel(j, i, int(matrix[i,j][0] * 255), int(matrix[i,j][1] * 255), int(matrix[i,j][2] * 255))
            offset_canvas.SetImage(matrix)
            c = time.time()
            log.debug(f"{b - a} step, {c - b} step")
            offset_canvas = self.matrix.SwapOnVSync(offset_canvas)
            
            now = time.time()
            t_last, wait_time = now, dt - (now - t_last)
            if wait_time < 0:
                log.warning(f"Frame dt exceeded: {wait_time}")
            else:
                log.debug(f"Sleeping for {wait_time}")
                time.sleep(wait_time)

        
if __name__ == "__main__":
    b = BaseMatrix()
    if not b.process():
        b.print_help()

