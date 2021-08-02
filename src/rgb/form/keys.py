#!/usr/bin/env python

import colorsys
import datetime
from rgb.form.keyawareform import KeyAwareForm
from rgb.utilities import hsv_to_pixel
import json
import logging
import math
import os
import random
import time
from abc import abstractproperty
from dataclasses import dataclass
from random import randrange
from typing import Dict, List, Set, Tuple

import numpy as np

from rgb.constants import MIDI_DIAL_MAX, NUM_NOTES
from PIL import Image
from rgb.form.baseform import BaseForm
from rgb.form.keyawareform import Press
from rgb.messages import Dial
from rgb.utilities import clamp

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))

class Keys(KeyAwareForm):

    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
            
    def step(self, dt) -> Image.Image:
        res = np.zeros((self.matrix_height, self.matrix_width, 3), dtype=np.uint8)
        xs = np.linspace(start=0, stop=self.matrix_width, num=NUM_NOTES + 1, endpoint=True, dtype=np.uint8)
        for v in self.presses.values():
            index = v.note_index
            hue = index / NUM_NOTES
            pixel = hsv_to_pixel(hue, 1.0, 1.0 if v else 0.0)
            lo = xs[index]
            hi = xs[index + 1] 
            res[:,lo:hi,:] = np.tile( pixel , (self.matrix_height, hi - lo, 1))
            
        return Image.fromarray(res) #.transpose(Image.FLIP_TOP_BOTTOM)

