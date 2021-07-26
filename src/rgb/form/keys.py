#!/usr/bin/env python

import colorsys
import datetime
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
import numpy.typing as npt
from constants import MIDI_DIAL_MAX, NUM_NOTES
from PIL import Image
from rgb.form.baseform import BaseForm
from rgb.form.keyawareform import Press
from rgb.messages import Dial
from rgb.utilities import clamp

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))

class KeyAwareForm(BaseForm):
    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
        self.presses = dict()

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

class Keys(KeyAwareForm):

    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
            
    def step(self, dt) -> Image.Image:
        res = np.zeros((self.matrix_height, self.matrix_width, 3), dtype=np.uint8)
        xs = np.linspace(start=0, stop=self.matrix_width, num=NUM_NOTES + 1, endpoint=True, dtype=np.uint8)
        for v in self.presses.values():
            index = v.note % NUM_NOTES
            hue = index / NUM_NOTES
            pixel = hsv_to_pixel(hue, 1.0, 1.0 if v else 0.0)
            lo = xs[index]
            hi = xs[index + 1] 
            res[:,lo:hi,:] = np.tile( pixel , (self.matrix_height, hi - lo, 1))
            
        return Image.fromarray(res) #.transpose(Image.FLIP_TOP_BOTTOM)
