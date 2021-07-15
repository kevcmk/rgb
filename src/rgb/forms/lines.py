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


MIDI_DIAL_MAX = 127
@dataclass
class Press():
    t: float
    note: int
    velocity: int
    x1: int
    y1: int
    x2: int
    y2: int
    fill: Tuple[int, int, int]

class Lines(Form):

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
            velocity = value['velocity'] / MIDI_DIAL_MAX
            
            hue = (note % Lines.NUM_NOTES) / Lines.NUM_NOTES
            rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            color = (int(255 * rgb[0]),int(255 * rgb[1]),int(255 * rgb[2]))
            case = random.randint(0,5)
            if case == 0:
                (x1, y1, x2, y2) = (random.randint(0,w), 0, 0, random.randint(0,h))
            elif case == 1:
                (x1, y1, x2, y2) = (random.randint(0,w), 0, self.matrix_height - 1, random.randint(0,self.matrix_height))
            self.presses[note] = Press(
                t=time.time(), 
                note=note, 
                velocity=velocity,
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2,
                fill=color
            )
        elif value['type'] == 'note_off':
            note = value['note']
            if note in self.presses:
                del self.presses[note]
        else:
            log.debug(f"Unhandled message: {value}")

    
        
        
    def step(self, dt) -> Image.Image:
        img = Image.new("RGB", (self.matrix_width, self.matrix_height))
        draw_context = ImageDraw.Draw(img)
        now = time.time()
        for press in sorted(self.presses.values(), key=lambda x: x.t):
            draw_context.line((press.x1,press.y1,press.x2,press.y2), fill=press.fill)
        # Return the vertical flip, origin at the top.
        return img


