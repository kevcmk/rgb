#!/usr/bin/env python

import colorsys
import json
import logging
import math
import os
import random
import time
from dataclasses import dataclass
from random import randrange
from typing import Dict, List, Set, Tuple

import numpy as np
import numpy.typing as npt
from PIL import Image, ImageDraw
from form import Form

from messages import Dial
from utilities import constrain

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))


MAX_MIDI_VELOCITY = 127
@dataclass
class Press():
    t: float
    note: int
    velocity: int
    bounding_circle_x: int
    bounding_circle_y: int
    bounding_circle_r: int
    n_sides: int
    rotation: int 
    fill: Tuple[int, int, int]

class Shape(Form):

    NUM_NOTES = 12

    def __init__(self, dimensions: Tuple[int, int]):
        (self.matrix_width, self.matrix_height) = dimensions
        self.presses = dict()
        self.grow = 0
        self.handlers = {
            "Dial": {
               #0: lambda state: self.adjust_ffw(state),
            }
        }
    
    def cleanup(self):
        self.presses = dict()
    
    def midi_handler(self, value: Dict):
        # Key Press: msg.dict() -> {'type': 'note_on', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0} {'type': 'note_off', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0}
        if value['type'] == 'note_on':
            note = value['note']
            velocity = value['velocity'] / MAX_MIDI_VELOCITY
            
            hue = (note % Shape.NUM_NOTES) / Shape.NUM_NOTES
            rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            color = (int(255 * rgb[0]),int(255 * rgb[1]),int(255 * rgb[2]))
            self.presses[note] = Press(
                t=time.time(), 
                note=note, 
                velocity=velocity,
                bounding_circle_x=random.randint(0,self.matrix_width),
                bounding_circle_y=random.randint(0,self.matrix_height),
                bounding_circle_r=random.randint(10,30),
                n_sides=random.randint(3, 9),
                rotation=random.randint(0, 360), 
                fill=color
            )
        elif value['type'] == 'note_off':
            note = value['note']
            if note in self.presses:
                del self.presses[note]
        if value['type'] == 'control_change' and value['control'] == 14: 
            self.grow = value['value'] / 4
        else:
            log.debug(f"Unhandled message: {value}")

    
        
        
    def step(self, dt) -> Image.Image:
        img = Image.new("RGB", (self.matrix_width, self.matrix_height))
        draw_context = ImageDraw.Draw(img)
        now = time.time()
        for press in sorted(self.presses.values(), key=lambda x: x.t):
            r = press.bounding_circle_r + (now - press.t) * self.grow
            draw_context.regular_polygon((press.bounding_circle_x,press.bounding_circle_y,r), press.n_sides, rotation=press.rotation, fill=press.fill, outline=None)
        # Return the vertical flip, origin at the top.
        return img


