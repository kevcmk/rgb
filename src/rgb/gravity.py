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

import numpy as np
import numpy.typing as npt

import constants
from messages import Dial
from utilities import constrain
from form import Form

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
    
class Gravity(Form):

    # Shape := The bounds of the random.uniform x velocity
    MAX_SHAPE = 0.002 # Random.uniform [-0.002, 0.002] m/s

    def __init__(self, dimensions: Tuple[int, int], meters_per_pixel: float, population: int):
        (self.matrix_width, self.matrix_height) = dimensions
        self.world_width = self.matrix_width * meters_per_pixel
        self.world_height = self.matrix_height * meters_per_pixel
        self.population = population
        self.gravitational_constant = -0.08
        self.shape = Gravity.MAX_SHAPE * 0.5
        self.particles: Set[Elt] = set()
          
        self.handlers = {
            "Button": {
                0: lambda state: self.button_0_handler(state),
                1: lambda state: self.button_1_handler(state)
            },
            "Dial": {
                0: lambda state: self.adjust_gravitational_constant(state),
            }
        }
    
    def midi_handler(self, value: Dict):
        # TODO
        if value['type'] == 'control_change' and value['control'] == 14: 
            self.adjust_gravitational_constant(value['value'] / constants.MIDI_DIAL_MAX)
        elif value['type'] == 'control_change' and value['control'] == 15:
            self.adjust_nozzle(value['value'] / constants.MIDI_DIAL_MAX)
    
    def button_0_handler(self, state: bool):
        if state:
            self.population = min(self.population + 1, 512)

    def button_1_handler(self, state: bool):
        if state:
            self.population = max(self.population - 1, 0)
    
    def adjust_gravitational_constant(self, state):
        """
        Logarithmic scale timespan for dial 
        
        State 0.0 := g = 0.05 m/s^2
        State 1.0 := g = 12 m/s^2
        """
        constrained = constrain(state, 0.0, 1.0)
        # math.exp(0) = 1.0
        # math.exp(2.5) = 12.18
        
        self.gravitational_constant = -(math.exp(2.5 * constrained) - 0.95)
    
    def adjust_nozzle(self, state):
        """
        Logarithmic scale timespan for dial 
        
        State 0.0 := g = 0.05 m/s^2
        State 1.0 := g = 12 m/s^2
        """
        constrained = constrain(state, 0.0, 1.0)
        # math.exp(0) = 1.0
        # math.exp(2.5) = 12.18
        
        self.shape = constrained * Gravity.MAX_SHAPE
    
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
                    vx=random.uniform(-self.shape, self.shape),
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
        return Image.fromarray(img).transpose(Image.FLIP_TOP_BOTTOM)

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

            # This one looks fluttery
            # elt.vy = elt.vy + 0.5 * -9.8 * (dt ** 2) # -9.8 m/s^2
            
            # It approximates to this: with g = 0.08
            elt.vy += dt * self.gravitational_constant

            # elt.vy = elt.vy + (-1.62 * dt) # Moon gravity
            # elt.vy = elt.vy + (-0.08 * dt) # Moon gravity
            elt.y = elt.y + (elt.vy * dt)
            log.debug(elt)
        self.particles = set(filter(lambda x: x.y >= 0, self.particles))
        return self._render()



