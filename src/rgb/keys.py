#!/usr/bin/env python

import random
import json
from typing import Dict, List, Set, Tuple
import math
from random import randrange
import time
from PIL import Image
from dataclasses import dataclass
import colorsys
import logging
import os
import math

import numpy as np
import numpy.typing as npt

from messages import Dial
from utilities import constrain

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))


MAX_MIDI_VELOCITY = 127

class Keys():
    def __init__(self, dimensions: Tuple[int, int]):
        (self.matrix_width, self.matrix_height) = dimensions
        self.keys = [0 for _ in range(12)]
        self.handlers = {
            "Dial": {
               #0: lambda state: self.adjust_ffw(state),
            }
        }
    
    def midi_handler(self, value: Dict):
        # Key Press: msg.dict() -> {'type': 'note_on', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0} {'type': 'note_off', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0}
        if value['type'] == 'note_on':
            index = value['note'] % 12
            self.keys[index] = value['velocity'] / MAX_MIDI_VELOCITY
        elif value['type'] == 'note_off':
            index = value['note'] % 12
            self.keys[index] = 0
        else:
            log.debug(f"Unhandled message: {value}")

    def step(self, dt) -> Image.Image:
        img = np.zeros((self.matrix_height, self.matrix_width, 3), dtype=np.uint8)
        xs = np.linspace(start=0, stop=self.matrix_width, num=len(self.keys) + 1, endpoint=True, dtype=np.uint8)
        for i, v in enumerate(self.keys):
            hue = i / len(self.keys)
            rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            pixel = (np.uint8(255 * rgb[0]),np.uint8(255 * rgb[1]),np.uint8(255 * rgb[2]))
            lo = xs[i]
            hi = xs[i + 1] 
            img[:,lo:hi,:] = np.tile( pixel , (self.matrix_height, hi - lo, 1))
                    
        # Return the vertical flip, origin at the top.
        return Image.fromarray(img) #.transpose(Image.FLIP_TOP_BOTTOM)


