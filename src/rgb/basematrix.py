

import json
import logging
import multiprocessing
import os
import sys
import time
from dataclasses import astuple, dataclass
from json.decoder import JSONDecodeError
from typing import Dict

import numpy as np
import numpy.typing as npt
from rgbmatrix import RGBMatrix, RGBMatrixOptions

import constants
import gravity
import hzel_samplebase
import imaqt
import keys
import orbit
import shape
import stars
import stripes
import timer
from messages import Button, Dial, Switch
from utilities import Dimensions

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))


class BaseMatrix(hzel_samplebase.SampleBase):

    def parse_hzeller_rgb_args(self):
        rgb_args = {k:v for k,v in os.environ.items() if k.startswith("RUN_ARG_")}
        for k,v in rgb_args.items():
            log.debug(f"Parsing rgb_arg: {k}: {v}")
            argparse_style_arg = "--" + k.replace("RUN_ARG_", "").replace("_", "-").lower()
            log.info(f"Arg-parsing: {argparse_style_arg}: {v}")
            sys.argv.extend([argparse_style_arg, v])

    def __init__(self, dimensions: Dimensions):
        super().__init__()
        
        self.parse_hzeller_rgb_args()
                    

    def run(self):

        log.info(f"Running {self.form} at maximum {self.max_hz} Hz...")
        offset_canvas = self.matrix.CreateFrameCanvas()

        t_start = time.time()
        t_last = t_start
        
        while True:

            now = time.time()
            total_elapsed_since_last_frame = now - t_last
            t_last, wait_time = now, self.max_dt - total_elapsed_since_last_frame
            if wait_time < 0:
                log.debug(f"Frame dt exceeded: {wait_time}")
            else:
                time.sleep(wait_time)    
            
            matrix = self.form.step(total_elapsed_since_last_frame)
            offset_canvas.SetImage(matrix)
            offset_canvas = self.matrix.SwapOnVSync(offset_canvas)
            
            while self.midi_receiver_cxn.poll(0):
                value = self.midi_receiver_cxn.recv()
                log.info(f"midi_receiver_cxn received: {value}")
                # If form midi handler goes firse, then a pad strike that is also a valid key press does not induce that form's key's effect.
                self.form.midi_handler(value)
                self.midi_handler(value)
            
            while self.clicker_receiver_cxn.poll(0):
                value = self.clicker_receiver_cxn.recv()
                log.info(f"clicker_receiver_cxn received: {value}")
                
                message_type = type(value).__name__
                index = value.index
                state = value.state
                
                log.info(f"{message_type} -> {index}, {state}")        
                for target in (self, self.form):
                    try:            
                        target.handlers[message_type][index](state)
                    except KeyError as e:
                        log.debug(f"No handler for {value} on {target}")
                        continue
                    else: 
                        # If a handler succeeds, break.
                        log.debug(f"Handler succeeded for {target}")
                        break

        
if __name__ == "__main__":
    b = BaseMatrix()
    if not b.process():
        b.print_help()

