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

import numpy as np
import numpy.typing as npt

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))

@dataclass
class Elt:
    def __init__(self, x, y, vx, vy):
        self.x: float = x
        self.y: float = y
        self.vx: float = vx
        self.vy: float = vy
        self.hue: float = random.random()
        
    def __str__(self):
        return json.dumps({key: getattr(self, key) for key in ["x","y","vx","vy"]})

    def __hash__(self):
        return hash((self.x, self.y, self.hue))
    
    def __eq__(self, other):
        return hash(self) == hash(other)
    
    @property
    def rgb(self) -> Tuple[np.uint8,np.uint8,np.uint8]:
        rgb = colorsys.hsv_to_rgb(self.hue, 1.0, 1.0)
        return (np.uint8(rgb[0] * 255),np.uint8(rgb[1] * 255),np.uint8(rgb[2] * 255))
    
class Gravity():
    def __init__(self, matrix_height: int, matrix_width: int, world_height: float, world_width: float, hz: float, population: int):
        self.hz = 60
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
        room = self.population - len(self.particles)
        if room <= 0:
            return
        births = random.randint(0, room)
        for i in range(births):
            self.particles.add(
                Elt(
                    x=self.world_width / 2,
                    y=self.world_height, 
                    vx=random.uniform(-0.002, 0.002),
                    vy=0
                )
            )

    def _render(self) -> Image.Image:
        img = np.zeros((self.matrix_height, self.matrix_width, 3), dtype=np.uint8)
        for elt in self.particles:
            
            render_y = round(self.matrix_scale * elt.y)
            render_x = round(self.matrix_scale * elt.x)
            
            if 0 <= render_y < self.matrix_height and \
                0 <= render_x < self.matrix_width:
                rgb = elt.rgb
                img[render_y,render_x,0] = rgb[0]
                img[render_y,render_x,1] = rgb[1]
                img[render_y,render_x,2] = rgb[2]
            # Else, skip it
        # Return the vertical flip, origin at the top.
        return Image.fromarray(img)

    def step(self, dt) -> Image.Image:
        self._populate_particles()
        for elt in self.particles:
            elt.x = elt.x + elt.vx

            if elt.x > self.world_width:
                elt.x = self.world_width - (elt.x - self.world_width)
                elt.vx = -elt.vx
            elif elt.x < 0:
                elt.x = -elt.x
                elt.vx = -elt.vx

            elt.vy = elt.vy + 0.5 * -9.8 * (dt ** 2) # -9.8 m/s^2
            # elt.vy = elt.vy + (-1.62 * dt) # Moon gravity
            # elt.vy = elt.vy + (-0.08 * dt) # Moon gravity
            elt.y = elt.y + (elt.vy * dt)
            log.debug(elt)
        self.particles = set(filter(lambda x: x.y >= 0, self.particles))
        return self._render()

    
       


# Main function
if __name__ == "__main__":
    gravity = Gravity()
    if not gravity.process():
        gravity.print_help()

