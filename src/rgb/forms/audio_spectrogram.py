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
import datetime
import constants
import numpy as np
import numpy.typing as npt
from PIL import Image
from form import Form

from messages import Dial
from utilities import constrain, clamped_add, clamped_subtract

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))


class AudioSpectrogram(Form):

    NUM_NOTES = 12
    
    def state_handler(self, spectrum: List[float]):
        log.warning(f"Max State: {max(spectrum)}")
        if self.state:
            self.state = [clamped_add(x,y) for x,y in zip(spectrum, self.state)]
        else:
            self.state = [min(1.0, x) for x in spectrum]
        

    def __init__(self, dimensions: Tuple[int, int]):
        self.decay_per_s = 2.0
        (self.matrix_width, self.matrix_height) = dimensions
        self.presses = dict()
        self.state = []
        self.handlers = {
            "Spectrum": {
                0: self.state_handler 
            }
        }

    def step(self, dt) -> Image.Image:
        decay = dt * self.decay_per_s
        self.state = [clamped_subtract(x, decay) for x in self.state]
        return self._render(dt)
    
    def _render(self, dt) -> Image.Image:
        img = np.zeros((self.matrix_height, self.matrix_width, 3), dtype=np.uint8)
        n = self.matrix_height
        xs = np.linspace(start=0, stop=self.matrix_width, num=n + 1, endpoint=True, dtype=np.uint8)
        for index, v in enumerate(self.state[:n]):
            x = index % 12
            hue = x / 12
            rgb = colorsys.hsv_to_rgb(hue, 1.0, v)
            pixel = (np.uint8(255 * rgb[0]),np.uint8(255 * rgb[1]),np.uint8(255 * rgb[2]))
            lo = xs[index]
            hi = xs[index + 1] 
            img[index,:,:] = np.tile( pixel , (self.matrix_width, 1))
        
        
        return Image.fromarray(img) #.transpose(Image.FLIP_TOP_BOTTOM)


