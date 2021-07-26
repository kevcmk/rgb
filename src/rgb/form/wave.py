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
import constants

import numpy as np
import numpy.typing as npt
from PIL import Image
from rgb.form.baseform import BaseForm

from rgb.messages import Dial
from rgb.utilities import clamp

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))


MIDI_DIAL_MAX = 127
@dataclass
class Press():
    t: float
    note: int
    velocity: int

class Wave(BaseForm):

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
            velocity = value['velocity'] / MIDI_DIAL_MAX
            self.presses[note] = Press(t=time.time(), note=note, velocity=velocity)
        elif value['type'] == 'note_off':
            note = value['note']
            if note in self.presses:
                del self.presses[note]
        else:
            log.debug(f"Unhandled message: {value}")

    @staticmethod    
    def normal_dist(x , mean , sd):
        prob_density = (np.pi*sd) * np.exp(-0.5*((x-mean)/sd)**2)
        return prob_density

    @staticmethod
    def v_to_rgb(v: float) -> Tuple[np.uint8, np.uint8, np.uint8]:
        rgb = colorsys.hsv_to_rgb(1.0, 1.0, v)
        return (np.uint8(255 * rgb[0]),np.uint8(255 * rgb[1]),np.uint8(255 * rgb[2]))

    # Horizontal
    def step(self, dt) -> Image.Image:
        img = np.zeros((self.matrix_height, self.matrix_width, 3), dtype=np.uint8)
        
        # for k, v in self.presses.items():
        #     index = k % Keys.NUM_NOTES
        #     hue = index / Keys.NUM_NOTES
        #     rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0 if v else 0.0)
        #     pixel = (np.uint8(255 * rgb[0]),np.uint8(255 * rgb[1]),np.uint8(255 * rgb[2]))
        #     lo = xs[index]
        #     hi = xs[index + 1] 
        #     img[:,lo:hi,:] = np.tile( pixel , (self.matrix_height, hi - lo, 1))


        x = np.linspace(0, self.matrix_width, self.matrix_width)
        linear = Wave.normal_dist(x, 0, 5.0)
        # Normalize between 0 and 1
        linear /= np.max(np.abs(linear),axis=0)
        
        linear_rgb = np.array(list(map(Wave.v_to_rgb, linear)))
        print("Linear rgb")
        print(linear_rgb)
        matrix_rgb = np.tile(linear_rgb, (self.matrix_height, 1, 1))
        print("Matrix rgb")
        print(matrix_rgb)

                    
        # Return the vertical flip, origin at the top.
        return Image.fromarray(matrix_rgb) #.transpose(Image.FLIP_TOP_BOTTOM)
