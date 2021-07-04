#!/usr/bin/env python

import colorsys
import json
import logging
import math
import os
import random
import time
from dataclasses import dataclass
from random import randrange
from typing import Dict, List, Set, Tuple

import numpy as np
import numpy.typing as npt
from PIL import Image
from form import Form

from messages import Dial
from utilities import constrain

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))


MAX_MIDI_VELOCITY = 127
@dataclass
class Press():
    t: float
    note: int
    velocity: int

class Keys(Form):

    NUM_NOTES = 12

    def __init__(self, dimensions: Tuple[int, int]):
        (self.matrix_width, self.matrix_height) = dimensions
        self.presses = dict()
        self.handlers = {
            "Dial": {
               #0: lambda state: self.adjust_ffw(state),
            }
        }
    
    def cleanup(self):
        self.presses = dict()
    
    def midi_handler(self, value: Dict):
        # Key Press: msg.dict() -> {'type': 'note_on', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0} {'type': 'note_off', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0}
        if value['type'] == 'note_on':
            note = value['note']
            velocity = value['velocity'] / MAX_MIDI_VELOCITY
            self.presses[note] = Press(t=time.time(), note=note, velocity=velocity)
        elif value['type'] == 'note_off':
            note = value['note']
            if note in self.presses:
                del self.presses[note]
        else:
            log.debug(f"Unhandled message: {value}")

    def step(self, dt) -> Image.Image:
        img = np.zeros((self.matrix_height, self.matrix_width, 3), dtype=np.uint8)
        xs = np.linspace(start=0, stop=self.matrix_width, num=Keys.NUM_NOTES + 1, endpoint=True, dtype=np.uint8)
        for k, v in self.presses.items():
            index = k % Keys.NUM_NOTES
            hue = index / Keys.NUM_NOTES
            rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0 if v else 0.0)
            pixel = (np.uint8(255 * rgb[0]),np.uint8(255 * rgb[1]),np.uint8(255 * rgb[2]))
            lo = xs[index]
            hi = xs[index + 1] 
            img[:,lo:hi,:] = np.tile( pixel , (self.matrix_height, hi - lo, 1))
                    
        # Return the vertical flip, origin at the top.
        return Image.fromarray(img) #.transpose(Image.FLIP_TOP_BOTTOM)

