#!/usr/bin/env python

import colorsys
from rgb.utilities import hue_to_pixel
import logging
import math
import os
import time
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

import numpy as np
from PIL import Image
from rgb.form.baseform import BaseForm
from rgb.utilities import clamp
from noise import snoise3, pnoise3
log = logging.getLogger(__name__)
log.setLevel(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))


MIDI_DIAL_MAX = 127
@dataclass
class Press():
    t: float
    note: int
    velocity: int

class BaseNoise(BaseForm):

    NOISE_FUNCTIONS = [snoise3, pnoise3]
    def __init__(self, dimensions: Tuple[int, int]):
        (self.matrix_width, self.matrix_height) = dimensions
        self.presses = dict()

        self.noise_function_index = 0
        self.scale = 1 / 24.0 # 1/48, [0.1, 10]
        self.octaves = 4 # 4, [1, 8]
        self.persistence = 0.0125 # 0.25, [0, 5]
        self.timescale = 0.5
        
        self.t_start = time.time()
        self.nmax = -100000
        self.nmin = 10000
        
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

    def noisexy(self, x, y, z) -> float:
        return self.NOISE_FUNCTIONS[self.noise_function_index](y * self.scale, x * self.scale, z * self.timescale, octaves=self.octaves, persistence=self.persistence)

    def noise_to_pixel(self, v: float):
        return (np.uint8(v * 255),np.uint8(v * 255),np.uint8(v * 255))
    
    def step(self, dt) -> Image.Image:
        res = np.zeros((self.matrix_height, self.matrix_width, 3), dtype=np.uint8)
        dt = time.time() - self.t_start
        for i in range(self.matrix_height):
            for j in range(self.matrix_width):
                v = self.noisexy(x=j, y=i, z=dt)
                res[i,j,:] = self.noise_to_pixel(v)
        
        return Image.fromarray(res) #.transpose(Image.FLIP_TOP_BOTTOM)


class ZNoise(BaseNoise):
    pass

class HueNoise(BaseNoise):

    def noise_to_pixel(self, v: float):
        return hue_to_pixel((v + 1.0) / 2, 1.0, 1.0)