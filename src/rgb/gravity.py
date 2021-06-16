#!/usr/bin/env python

import random
import json
from typing import List, Set, Tuple
import math
from random import randrange
import time
from samplebase import SampleBase
from dataclasses import dataclass
import colorsys
import logging
import os

import numpy as np
import numpy.typing as npt

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))

@dataclass
class Elt:
    def __init__(self, y, x):
        self.y: float = y
        self.x: float = x
        self.vy: float = 0
        self.hue: float = random.random()
        
    def __str__(self):
        return json.dumps({key: getattr(self, key) for key in ["x","y","vy"]})

    def __hash__(self):
        return hash((self.x, self.y, self.hue))
    
    def __eq__(self, other):
        return hash(self) == hash(other)
    
    @property
    def hsv(self):
        return colorsys.hsv_to_rgb(self.hue, 1.0, 1.0)
    
class Gravity():
    def __init__(self, matrix_height: int, matrix_width: int, world_height: float, world_width: float, hz: float, population: int):
        self.hz = 60
        self.steps = 250
        self.matrix_height = matrix_height
        self.matrix_width = matrix_width
        self.world_height = world_height # Meters 32x5mm
        self.world_width = world_width # Meters 32x5mm
        self.population = population
        self.particles: Set[Elt] = set()
    
    @property
    def matrix_scale(self) -> float:
        # E.g. 1:4 would be 0.25
        return self.matrix_height / float(self.world_height)

    def _populate_particles(self):
        room = random.randint(0, self.population - len(self.particles))
        for i in range(room):
            self.particles.add(
                Elt(
                    y=self.world_height, 
                    x=random.uniform(0, self.world_width),
                ) 
            )

    def _render(self):
        img = np.zeros((self.matrix_height, self.matrix_width, 3))
        for elt in self.particles:
            
            render_y = round(self.matrix_scale * elt.y)
            render_x = round(self.matrix_scale * elt.x)
            
            if 0 <= render_y < self.matrix_height and \
                0 <= render_x < self.matrix_width:
                img[render_y,render_x,:] = elt.hsv
            # Else, skip it
        # Return the vertical flip, origin at the top.
        return img

    def step(self, dt) -> np.ndarray:
        self._populate_particles()
        for elt in self.particles:
            # elt.vy = elt.vy + (-9.8 * dt) # -9.8 m/s^2
            elt.vy = elt.vy + (-1.62 * dt) # Moon gravity
            elt.y = elt.y + (elt.vy * dt)
        self.particles = set(filter(lambda x: x.y >= 0, self.particles))
        return self._render()

    
       


# Main function
if __name__ == "__main__":
    gravity = Gravity()
    if not gravity.process():
        gravity.print_help()
