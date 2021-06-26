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

from messages import Dial
from utilities import constrain

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
class Body:
    def __init__(self, name, color, x, y, vx, vy, mass):
        self.name: str = name
        self.color: Tuple[int,int,int] = color
        self.x: float = x
        self.y: float = y
        self.vx: float = vx
        self.vy: float = vy
        self.mass: float = mass
        self.hue: float = random.random()
        
    def __str__(self):
        return json.dumps({key: getattr(self, key) for key in ["name", "x","y","vx","vy", "mass"]})

    def __hash__(self):
        return hash((self.x, self.y, self.hue))
    
    def __eq__(self, other):
        return hash(self) == hash(other)
    
    @property
    def rgb(self) -> Tuple[np.uint8,np.uint8,np.uint8]:
        rgb = colorsys.hsv_to_rgb(self.hue, 1.0, 1.0)
        return (np.uint8(self.color[0]),np.uint8(self.color[1]),np.uint8(self.color[2]))
    
class Orbit():
    def __init__(self, dimensions: Tuple[int, int], fast_forward_scale: float):
        self.fast_forward_scale = fast_forward_scale
        (self.matrix_width, self.matrix_height) = dimensions
        h_to_w_ratio = (self.matrix_height / self.matrix_width) # h:w ratio
        self.world_width = MARS_APHELION_METERS * 2
        self.world_height = self.world_width * h_to_w_ratio 
        sun = Body(name="Sun", color=(255,255,0), x=self.world_width / 2, y = self.world_height / 4, vx = 0, vy = 0, mass=SUN_MASS_KILOGRAMS)
        earth = Body(name="Earth", color=(64,64,255), x=self.world_width / 2, y=sun.y - EARTH_PERIHELION_METERS, vx=EARTH_PERIHELION_VELOCITY_MS, vy=0, mass = EARTH_MASS_KILOGRAMS)
        mars = Body(name="Mars", color=(255,64,0), x=self.world_width / 2, y=sun.y + MARS_PERIHELION_METERS, vx=-MARS_PERIHELION_VELOCITY_MS, vy=0, mass = MARS_MASS_KILOGRAMS)
        moon = Body(name="Moon", color=(180,180,180), x=self.world_width / 2, y = earth.y + MOON_PERIGEE_METERS, vx = earth.vx + MOON_PERIGEE_VELOCITY_MS, vy = 0, mass=MOON_MASS_KILOGRAMS)
        self.bodies: Set[Body] = {
            earth,
            mars,
            moon,
            sun,
        }
                 
        self.handlers = {
            "Dial": {
                0: lambda state: self.adjust_ffw(state),
            }
        }

    def adjust_ffw(self, state):
        """
        Logarithmic scale timespan for dial 
        
        State 0.0 := 1 second per second 
        State 1.0 := 1 year per second
        """
        constrained = constrain(state, 0.0, 1.0) 
        # In [12]: math.log(60 * 60 * 24 * 365)
        # Out[12]: 17.26664030837464
        self.fast_forward_scale = math.exp(constrained * 17.26664)
        log.debug(f"Adjusting orbit's .ffw state: {state}, constrained {constrained}, .ffw {self.fast_forward_scale}")
    
    @property
    def matrix_scale(self) -> float:
        # E.g. 1:4 would be 0.25
        return self.matrix_height / float(self.world_height)

    def _render(self) -> Image.Image:
        img = np.zeros((self.matrix_height, self.matrix_width, 3), dtype=np.uint8)
        for a in self.bodies:
            
            render_x = round(self.matrix_scale * a.x)
            render_y = round(self.matrix_scale * a.y)
            if 0 <= render_y < self.matrix_height and \
                0 <= render_x < self.matrix_width:
                rgb = a.rgb
                img[render_y,render_x,0] = rgb[0]
                img[render_y,render_x,1] = rgb[1]
                img[render_y,render_x,2] = rgb[2]
            # Else, skip it
        
        # Return the vertical flip, origin at the top.
        return Image.fromarray(img) #.transpose(Image.FLIP_TOP_BOTTOM)

    def step(self, dt) -> Image.Image:
        for a in self.bodies:
            # log.debug(a)
            fxs = []
            fys = []
            for b in self.bodies:
                if a == b:
                    continue
                distance_squared = (a.x - b.x) ** 2 + (a.y - b.y) ** 2
                f = GRAVITATIONAL_CONSTANT * a.mass * b.mass / distance_squared
                theta = math.atan2(b.y - a.y, b.x - a.x)
                fxs.append(math.cos(theta) * f)
                fys.append(math.sin(theta) * f)
            fx = sum(fxs)
            fy = sum(fys)
            ax = fx / a.mass
            ay = fy / a.mass
            actual_elapsed_time = dt * self.fast_forward_scale
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