#!/usr/bin/env python

import colorsys
import logging
import math
import os
import random
import time
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict, Tuple, Union

import numpy as np
from rgb.form.baseform import BaseForm
from PIL import Image, ImageDraw, ImageFont
from rgb.utilities import constrain

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))


MIDI_DIAL_MAX = 127
@dataclass
class Press():
    t: float
    note: int
    velocity: int
    position_x: int
    position_y: int
    radius: int
    color: Tuple[int, int, int]

    @property
    def num_sides(self):
        return int(((self.t * 100) % 8))
    
    @property
    def rotation(self):
        return int(((self.t * 1000) % 1000) * 360)
        

class RandomShape(BaseForm):

    NUM_NOTES = 12

    def __init__(self, dimensions: Tuple[int, int]):
        (self.matrix_width, self.matrix_height) = dimensions
        self.presses: Dict[str, Press] = dict()
        self.grow = 0
        # The logarithmic base of the grow rate of a shape. High notes grow faster than low notes, a low base means the differences between high and low notes are more apparent.
        self.grow_ratio_logarithmic_base = 2
        # The logarithmic base of the size of a shape. High notes are smaller than low notes, a low base means the differences between high and low notes are more apparent.
        self.shape_ratio = 2
        self.handlers = {
            "Dial": {
               #0: lambda state: self.adjust_ffw(state),
            }
        }
    
    def cleanup(self):
        self.presses = dict()

    @staticmethod
    def calculate_radius(p: Press, grow_rate: float, t: float) -> float:
        note_growfactor = math.log(p.note, grow_rate)
        return p.radius + (t - p.t) * note_growfactor + 1
    
    def midi_handler(self, value: Dict):
        # Key Press: msg.dict() -> {'type': 'note_on', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0} {'type': 'note_off', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0}
        if value['type'] == 'note_on':
            note = value['note']
            velocity = value['velocity'] / MIDI_DIAL_MAX
            # 21 , 108
            hue = (note % RandomShape.NUM_NOTES) / RandomShape.NUM_NOTES
            rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            color = (int(255 * rgb[0]),int(255 * rgb[1]),int(255 * rgb[2]))
            self.presses[note] = Press(
                t=time.time(), 
                note=note, 
                velocity=velocity,
                position_x=random.randint(0,self.matrix_width),
                position_y=random.randint(0,self.matrix_height),
                radius=int(5 * math.log(109 - note, self.shape_ratio) + 1),
                color=color
            )
        elif value['type'] == 'note_off':
            note = value['note']
            if note in self.presses:
                del self.presses[note]
        elif value['type'] == 'control_change' and value['control'] == 14: 
            self.grow = value['value'] / 4
            log.debug('Grow: {self.grow}')
        elif value['type'] == 'control_change' and value['control'] == 15: 
            self.grow_ratio_logarithmic_base = max(2 / 32, (value['value'] / 32)) + 1
            log.debug('Grow Ratio: {self.grow_ratio}')
        elif value['type'] == 'control_change' and value['control'] == 16: 
            self.shape_ratio = max(2 / 32, (value['value'] / 32)) + 1
            log.debug('Grow Ratio: {self.grow_ratio}')
        else:
            log.debug(f"Unhandled message: {value}")

    def step(self, dt: float) -> Union[Image.Image, np.ndarray]:
        img = Image.new("RGB", (self.matrix_width, self.matrix_height))
        draw_context = ImageDraw.Draw(img)
        now = time.time()
        for press in sorted(self.presses.values(), key=lambda x: x.t):
            note_growfactor = math.log(press.note, self.grow_ratio_logarithmic_base)
            r = press.radius + (now - press.t) * (self.grow * note_growfactor) + 1
            self.draw_shape(draw_context, press, r)
        # Return the vertical flip, origin at the top.
        return img

    @abstractmethod
    def draw_shape(self, draw_context, press: Press, r: float):
        pass
    

class RandomOutlineCircle(RandomShape):
    def draw_shape(self, draw_context: ImageDraw.ImageDraw, press: Press, r: float):
        draw_context.ellipse((press.position_x - r, press.position_y - r, press.position_x + r, press.position_y + r), fill=None, outline=press.color)

class RandomOutlineShape(RandomShape):
    def draw_shape(self, draw_context: ImageDraw.ImageDraw, press: Press, r: float):
        draw_context.regular_polygon((press.position_x,press.position_y,r), press.num_sides, rotation=press.rotation, fill=press.color, outline=None)
        
class RandomIcon(RandomShape):

    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
        self.icon_size = 18
        self.font = ImageFont.truetype("src/rgb/fonts/DejaVuSans.ttf", self.icon_size)
        self.palette = "⤬⤯★✶✢❤︎✕⨳⩕⩙♚♛♜♝♞♟♔♕♖♗♘♙♈︎♉︎♊︎♋︎♌︎♍︎♎︎♏︎♐︎♑︎♒︎♓︎☉☿♀︎♁♂︎♃♄♅♆⚕︎⚚☯︎⚘✦✧⚡︎"
        
    def draw_shape(self, draw_context: ImageDraw.ImageDraw, press: Press, r: float):
        x = press.position_x
        y = press.position_y
        elt_index = int((press.t % 1) * len(self.palette))
        elt = self.palette[elt_index]
        draw_context.text((x,y), 
            text=elt, 
            fill=(255, 0, 0), 
            anchor="mm",
            font=self.font
        )
        