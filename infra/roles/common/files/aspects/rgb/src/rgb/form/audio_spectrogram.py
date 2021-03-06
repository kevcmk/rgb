#!/usr/bin/env python

import colorsys
from rgb.constants import MIDI_DIAL_MAX
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
import numpy as np

from PIL import Image
from rgb.form.baseform import BaseForm

from rgb.messages import Dial
from rgb.utilities import clamp, clamped_add, clamped_subtract

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))


class AudioSpectrogram(BaseForm):
    def state_handler(self, spectrum: List[float]):
        log.warning(f"Max State: {max(spectrum)}")
        if self.state:
            self.state = [clamped_add(x, y * self.gain) for x, y in zip(spectrum, self.state)]
        else:
            self.state = [min(1.0, x) for x in spectrum]

    def __init__(self, dimensions: Tuple[int, int]):
        self.decay_per_s = 2.0
        (self.matrix_width, self.matrix_height) = dimensions
        self.last_observed_lo_dial = 0
        self.last_observed_hi_dial = 127
        self.gain = 1.0
        self.state = [random.random() for i in range(150)]
        self.handlers = {"Spectrum": {0: self.state_handler}}

    @property
    def last_observed_lo_dial(self):
        return BaseForm.dials(0)

    @property
    def last_observed_hi_dial(self):
        return BaseForm.dials(1)

    @property
    def decay_per_s(self):
        return BaseForm.dials(2) * 4

    @property
    def gain(self):
        return BaseForm.dials(3) * 2

    def step(self, dt) -> Image.Image:
        decay = dt * self.decay_per_s
        self.state = [clamped_subtract(x, decay) for x in self.state]
        return self._render(dt)

    def _render(self, dt) -> Image.Image:
        img = np.zeros((self.matrix_height, self.matrix_width, 3), dtype=np.uint8)
        effective_lo = min(self.last_observed_lo_dial, self.last_observed_hi_dial)
        effective_hi = max(self.last_observed_lo_dial, self.last_observed_hi_dial)
        if effective_lo == effective_hi:
            # Prevent both occupying same spot
            effective_hi += 1
        effective_span = effective_hi - effective_lo
        xs = np.linspace(start=0, stop=self.matrix_height, num=effective_span + 1, endpoint=True, dtype=np.uint8)
        for index, v in enumerate(reversed(self.state[effective_lo:effective_hi])):
            lo = xs[index]
            hi = xs[index + 1]
            if hi - lo == 0:
                continue
            x = index % 12
            hue = x / 12
            rgb = colorsys.hsv_to_rgb(hue, 1.0, v)
            pixel = (np.uint8(255 * rgb[0]), np.uint8(255 * rgb[1]), np.uint8(255 * rgb[2]))
            img[lo:hi, :, :] = np.tile(pixel, (hi - lo, self.matrix_width, 1))

        return Image.fromarray(img)  # .transpose(Image.FLIP_TOP_BOTTOM)
