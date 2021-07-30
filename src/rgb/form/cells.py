#!/usr/bin/env python

from rgb.form.basenoise import BaseNoise
import logging
import os
import time
from dataclasses import dataclass
from random import randrange
from typing import Dict, List, Set, Tuple

import numpy as np
import numpy.typing as npt
from constants import MIDI_DIAL_MAX, NUM_NOTES
from PIL import Image
from rgb.form.baseform import BaseForm
from rgb.form.keyawareform import KeyAwareForm, Press
from rgb.messages import Dial
from rgb.utilities import clamp, dial, hsv_to_pixel

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))

class Cells(KeyAwareForm):

    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
        self.cell_width = 8
        self.z = 0
    
    @property
    def practical_width(self) -> int:
        return self.matrix_width // self.cell_width
    
    @property
    def practical_height(self) -> int:
        return self.matrix_height // self.cell_width

    def midi_handler(self, value: Dict):
        super().midi_handler(value)
        if dial(0, value):
            self.scale = (value['value'] / MIDI_DIAL_MAX) ** 3 # [0, 1.0] 🏒🏒 
            log.info(f"Scale set to {self.scale}")
            
    def step(self, dt) -> Image.Image:
        
        # intensities = np.zeros((self.practical_height, self.practical_width), dtype=float)
        res = np.zeros((self.practical_height, self.practical_width, 3), dtype=np.uint8)
        # for i in range(self.practical_height):
        #     for j in range(self.practical_width):
        #         # practical_center = (i * self.cell_width + self.cell_width // 2, j * self.cell_width + self.cell_width // 2)
        #         # noise = self.select_noise(*practical_center, self.z)
        #         noise = self.select_noise(i, j, self.z)
        #         normalized_noise = self.normalize_noise(noise)
        #         intensities[i,j] = normalized_noise
        #         res[i,j,:] = hsv_to_pixel(0, 0, normalized_noise)
        
        for v in self.presses.values():
            x_index = hash(v.t) % self.practical_width
            y_index = hash(v.t) % self.practical_height
            index = v.note % NUM_NOTES
            hue = index / NUM_NOTES
            pixel = hsv_to_pixel(hue, 1.0, 1.0)
            res[y_index,x_index,:] = pixel
        image_small = Image.fromarray(res)
        resized = image_small.resize((self.matrix_width, self.matrix_height), resample=0)
        return resized

class CellsRun(Cells):
    pass