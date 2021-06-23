#!/usr/bin/env python

import random
import json
from typing import List, Set, Tuple
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

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))

EARTH_ORBITAL_VELOCITY_KMS = 2.978e4
SUN_MASS_KILOGRAMS = 1.989e30
EARTH_MASS_KILOGRAMS = 5.972e24
EARTH_ORBIT_METERS = 1.496e11
GRAVITATIONAL_CONSTANT = 6.67408e-11



@dataclass
class Elt:
    def __init__(self, x, y, vx, vy, mass):
        self.x: float = x
        self.y: float = y
        self.vx: float = vx
        self.vy: float = vy
        self.mass: float = mass
        self.hue: float = random.random()
        
    def __str__(self):
        return json.dumps({key: getattr(self, key) for key in ["x","y","vx","vy", "mass"]})

    def __hash__(self):
        return hash((self.x, self.y, self.hue))
    
    def __eq__(self, other):
        return hash(self) == hash(other)
    
    @property
    def rgb(self) -> Tuple[np.uint8,np.uint8,np.uint8]:
        rgb = colorsys.hsv_to_rgb(self.hue, 1.0, 1.0)
        return (np.uint8(rgb[0] * 255),np.uint8(rgb[1] * 255),np.uint8(rgb[2] * 255))
    
class Orbit():
    def __init__(self, matrix_height: int, matrix_width: int, hz: float, ffw: float):
        self.hz = hz
        self.ffw = ffw
        self.matrix_height = matrix_height
        self.matrix_width = matrix_width
        h_to_w_ratio = (self.matrix_height / self.matrix_width) # h:w ratio
        self.world_width = EARTH_ORBIT_METERS
        self.world_height = EARTH_ORBIT_METERS * h_to_w_ratio 
        self.bodies: Set[Elt] = {
            Elt(x=self.world_width / 2, y = self.world_height / 4, vx = 0, vy = 0, mass=SUN_MASS_KILOGRAMS),
            Elt(x=self.world_width / 2, y=0, vx=EARTH_ORBITAL_VELOCITY_KMS, vy=0, mass = EARTH_MASS_KILOGRAMS) # Earth is 333000
        }
    
    @property
    def matrix_scale(self) -> float:
        # E.g. 1:4 would be 0.25
        return self.matrix_height / float(self.world_height)

    def _render(self) -> Image.Image:
        img = np.zeros((self.matrix_height, self.matrix_width, 3), dtype=np.uint8)
        for a in self.bodies:
            
            render_x = round(self.matrix_scale * a.x)
            render_y = round(self.matrix_scale * a.y)
            log.info((render_x, render_y))
            
            if 0 <= render_y < self.matrix_height and \
                0 <= render_x < self.matrix_width:
                rgb = a.rgb
                img[render_y,render_x,0] = rgb[0]
                img[render_y,render_x,1] = rgb[1]
                img[render_y,render_x,2] = rgb[2]
            # Else, skip it
        
        # Return the vertical flip, origin at the top.
        return Image.fromarray(img).transpose(Image.FLIP_TOP_BOTTOM)

    def step(self, dt) -> Image.Image:
        for a in self.bodies:
            log.debug(a)
            for b in self.bodies:
                if a == b:
                    continue
                distance_squared = (a.x - b.x) ** 2 + (a.y - b.y) ** 2
                f = GRAVITATIONAL_CONSTANT * a.mass * b.mass / distance_squared
                
                theta = math.atan2(b.y - a.y, b.x - a.x)
                ax = math.cos(theta) * f / a.mass
                ay = math.sin(theta) * f / a.mass
                actual_elapsed_time = dt * self.ffw
                a.vx += ax * actual_elapsed_time
                a.vy += ay * actual_elapsed_time
                a.x += a.vx * actual_elapsed_time
                a.y += a.vy * actual_elapsed_time

        return self._render()

    
"""
In [8]: math.atan2(1.414, 1.414) / math.pi
Out[8]: 0.25

In [9]: math.atan2(-1.414, 1.414) / math.pi
Out[9]: -0.25

In [10]: math.atan2(-1.414, -1.414) / math.pi
Out[10]: -0.75

In [11]: math.atan2(1.414, -1.414) / math.pi
Out[11]: 0.75
"""