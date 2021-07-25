#!/usr/bin/env python

import colorsys
import logging
import math
import os
import time
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

import numpy as np
from PIL import Image
from rgb.form.baseform import BaseForm
from rgb.utilities import constrain
from noise import snoise3
log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))


MIDI_DIAL_MAX = 127
@dataclass
class Press():
    t: float
    note: int
    velocity: int

class KNoise(BaseForm):


    def __init__(self, dimensions: Tuple[int, int]):
        (self.matrix_width, self.matrix_height) = dimensions
        self.presses = dict()
        self.scale = 1 # [0.1, 10]
        self.octaves = 4 # [1, 8]
        self.persistence = 0.25 # [0, 5]
        self.t_start = time.time()

        self.x = np.arange(0, self.matrix_width, 1)
        self.y = np.arange(0, self.matrix_height, 1)
        self.xx, self.yy = np.meshgrid(self.x, self.y, sparse=False)
        
    
    def cleanup(self):
        self.presses = dict()

    
    def midi_handler(self, value: Dict):
        # Key Press: msg.dict() -> {'type': 'note_on', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0} {'type': 'note_off', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0}
        
        if value['type'] == 'note_on':
            note = value['note']
            velocity = value['velocity'] / MIDI_DIAL_MAX
            self.presses[note] = Press(t=time.time(), 
            note=note, 
            velocity=velocity)
        elif value['type'] == 'note_off':
            note = value['note']
            if note in self.presses:
                del self.presses[note]
        elif value['type'] == 'control_change' and value['control'] == 14: 
            self.wave_speed = 2 * value['value']
        elif value['type'] == 'control_change' and value['control'] == 15:
            self.wave_step = int(value['value'] / 4) + 1
        elif value['type'] == 'control_change' and value['control'] == 16:
            self.wave_width = min(
                int(math.log(value['value'] + 1)), 
                self.wave_step
            )
        elif value['type'] == 'control_change' and value['control'] == 16:
            self.wave_width = min(
                int(math.log(value['value'] + 1)), 
                self.wave_step
            )
    
        else:
            log.debug(f"Unhandled message: {value}")

    def step(self, dt) -> Image.Image:
        res = np.zeros((self.matrix_height, self.matrix_width, 3), dtype=np.uint8)
        dt = time.time() - self.t_start
        
        # img = np.sin(xx**2 + yy**2) / (xx**2 + yy**2)
        _vsnoise3 = np.vectorize(
            lambda x,y: np.uint8(snoise3(y * self.scale, x * self.scale, dt, octaves=self.octaves, persistence=self.persistence) * 255.0)
        )
        img = _vsnoise3(self.xx, self.yy)
        
        return Image.fromarray(img) #.transpose(Image.FLIP_TOP_BOTTOM)


