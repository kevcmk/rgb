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
from rgb.form.baseform import BaseForm

import numpy as np
import numpy.typing as npt

from messages import Dial
from utilities import clamp

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))


# Source https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html
# Source https://nssdc.gsfc.nasa.gov/planetary/factsheet/marsfact.html
# Source https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html

MARS_APHELION_METERS = 2.49229e11

EARTH_PERIHELION_VELOCITY_MS = 3.029e4
MOON_PERIGEE_VELOCITY_MS = 1.082e3
MARS_PERIHELION_VELOCITY_MS = 2.650e4

MOON_MASS_KILOGRAMS = 7.347e22
EARTH_MASS_KILOGRAMS = 5.972e24
MARS_MASS_KILOGRAMS = 6.417e23
SUN_MASS_KILOGRAMS = 1.989e30

MOON_PERIGEE_METERS = 3.633e8
EARTH_PERIHELION_METERS = 1.47092e11
MARS_PERIHELION_METERS = 2.06617e11
GRAVITATIONAL_CONSTANT = 6.67408e-11


@dataclass
class Stripe:
    def __init__(self, x, hue, velocity):
        self.x: float = x
        self.hue: float = hue
        self.hue_velocity = velocity
        
    def __str__(self):
        return json.dumps({key: getattr(self, key) for key in ["name", "x","y","vx","vy", "mass"]})

    def __hash__(self):
        return hash((self.x, self.hue))
    
    def __eq__(self, other):
        return hash(self) == hash(other)
    
    @property
    def rgb(self) -> Tuple[np.uint8,np.uint8,np.uint8]:
        rgb = colorsys.hsv_to_rgb(self.hue, 1.0, 1.0)
        return (np.uint8(255 * rgb[0]),np.uint8(255 * rgb[1]),np.uint8(255 * rgb[2]))

class Stripes(BaseForm):
    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
        self.stripes = [
            Stripe(x=i, hue=random.random(), velocity=random.uniform(-0.01, 0.01)) for i in range(self.matrix_width)
        ]         
        self.handlers = {
            "Dial": {
               #0: lambda state: self.adjust_ffw(state),
            }
        }
    
    def midi_handler(self, value: Dict):
        pass

    def step(self, dt) -> Image.Image:
        img = np.zeros((self.matrix_height, self.matrix_width, 3), dtype=np.uint8)
        for s in self.stripes:
            s.hue = (s.hue + s.hue_velocity) % 1.0
            img[:,s.x,:] = np.tile( s.rgb , (self.matrix_height,1))
                    
        # Return the vertical flip, origin at the top.
        return Image.fromarray(img) #.transpose(Image.FLIP_TOP_BOTTOM)


