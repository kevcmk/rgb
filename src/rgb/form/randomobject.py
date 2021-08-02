#!/usr/bin/env python

import colorsys
from rgb.form.keyawareform import Press
from rgb.utilities import get_dictionary
from rgb.utilities import get_font
import logging
import math
import os
import random
import time
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict, Tuple, Union
from rgb.constants import NUM_NOTES, NUM_PIANO_KEYBOARD_KEYS, MIDI_DIAL_MAX

import numpy as np
from rgb.form.baseform import BaseForm
from PIL import Image, ImageDraw, ImageFont
from rgb.utilities import clamp

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))

class SimpleSustainObject(BaseForm):

    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
        self.presses: Dict[str, Press] = dict()
        self.scale = 4 # Currently only for text size
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

    def calculate_radius(self, p: Press, shape_ratio: float, grow_ratio_logarithmic_base: float, current_time: float) -> float:
        note = p.note
        base_radius = int(5 * math.log(109 - note, shape_ratio) + 1)
        note_growfactor = math.log(p.note, grow_ratio_logarithmic_base)
        return base_radius + (current_time - p.t) * note_growfactor + 1
    
    def calculate_color(self, p: Press):
        hue = (p.note % NUM_NOTES) / NUM_NOTES
        rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        return (int(255 * rgb[0]), int(255 * rgb[1]), int(255 * rgb[2]))
    
    def calculate_xy_fractional_position(self, p: Press) -> Tuple[float, float]:
        # Return the floating point fractional [0,1] within the matrix width and height
        position_x = (hash(p.t) % 2048) / 2048 
        position_y = (hash(p.t) % 4096) / 4096
        return (position_x, position_y)
    
    def calculate_xy_position(self, p: Press) -> Tuple[int, int]:
        fractional_x, fractional_y = self.calculate_xy_fractional_position(p)
        return (int(fractional_x * self.matrix_width), int(fractional_y * self.matrix_height))

    def midi_handler(self, value: Dict):
        # Key Press: msg.dict() -> {'type': 'note_on', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0} {'type': 'note_off', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0}
        if value['type'] == 'note_on':
            note = value['note']
            velocity = value['velocity'] / MIDI_DIAL_MAX
            # 21 , 108
            self.presses[note] = Press(
                t=time.time(), 
                note=note, 
                velocity=velocity,
            )
        elif value['type'] == 'note_off':
            note = value['note']
            if note in self.presses:
                del self.presses[note]
        elif value['type'] == 'control_change' and value['control'] == 14:
            self.scale = value['value']
        elif value['type'] == 'control_change' and value['control'] == 15: 
            self.grow = value['value'] / 4
            log.debug('Grow: {self.grow}')
        elif value['type'] == 'control_change' and value['control'] == 16: 
            self.grow_ratio_logarithmic_base = max(2 / 32, (value['value'] / 32)) + 1
            log.debug('Grow Ratio: {self.grow_ratio}')
        elif value['type'] == 'control_change' and value['control'] == 17: 
            self.shape_ratio = max(2 / 32, (value['value'] / 32)) + 1
            log.debug('Grow Ratio: {self.grow_ratio}')
        else:
            log.debug(f"Unhandled message: {value}")

    def step(self, dt: float) -> Union[Image.Image, np.ndarray]:
        img = Image.new("RGB", (self.matrix_width, self.matrix_height))
        draw_context = ImageDraw.Draw(img)
        now = time.time()
        for press in sorted(self.presses.values(), key=lambda x: x.t):
            r = self.calculate_radius(press, self.shape_ratio, self.grow_ratio_logarithmic_base, current_time=now)
            self.draw_shape(draw_context, press, r)
        # Return the vertical flip, origin at the top.
        return img

    @abstractmethod
    def draw_shape(self, draw_context, press: Press, r: float):
        pass

class VerticalKeys(SimpleSustainObject):
    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
        # 0 until 1 before matrix_width, num keys + 1 steps (because we index [i,i+1]
        self.x_coords = np.linspace(0, self.matrix_width - 1, NUM_PIANO_KEYBOARD_KEYS + 1, dtype=np.uint8)
    def draw_shape(self, draw_context: ImageDraw.ImageDraw, press: Press, r: float):
        (x, y) = self.calculate_xy_position(press)
        color = self.calculate_color(press)
        lo = self.x_coords
        draw_context.rectangle((x - r, y - r, x + r, y + r), fill=None, outline=color)

class RandomOutlineCircle(SimpleSustainObject):
    def draw_shape(self, draw_context: ImageDraw.ImageDraw, press: Press, r: float):
        (x, y) = self.calculate_xy_position(press)
        color = self.calculate_color(press)
        draw_context.ellipse((x - r, y - r, x + r, y + r), fill=None, outline=color)

class RandomOutlineShape(SimpleSustainObject):
    def draw_shape(self, draw_context: ImageDraw.ImageDraw, press: Press, r: float):
        (x, y) = self.calculate_xy_position(press)
        color = self.calculate_color(press)
        num_sides = int(((press.t * 100) % 5) + 3)
        rotation = ((press.t * 1000) % 1000) * 360
        draw_context.regular_polygon((x, y, r), num_sides, rotation=rotation, fill=None, outline=color)
        
class RandomSolidShape(SimpleSustainObject):
    def draw_shape(self, draw_context: ImageDraw.ImageDraw, press: Press, r: float):
        (x, y) = self.calculate_xy_position(press)
        color = self.calculate_color(press)
        num_sides = int(((press.t * 100) % 5) + 3)
        rotation = ((press.t * 1000) % 1000) * 360
        draw_context.regular_polygon((x, y, r), num_sides, rotation=rotation, fill=color, outline=None)
     
class RandomText(SimpleSustainObject):
    # TODO Make abstract?
    def select_string(self, press: Press) -> str:
        raise NotImplementedError

    def font_cache(self, size: int): 
        if size in self._fonts:
            return self._fonts[size]
        else:
            log.info(f"Adding {size} to font_cache, size {len(self._fonts)}")
            self._fonts[size] = get_font(self.font_name, int(size))
            return self._fonts[size]
        
    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
        self.font_name = "DejaVuSans.ttf"
        self._fonts: Dict[int, ImageFont.FreeTypeFont] = dict()

    def draw_shape(self, draw_context: ImageDraw.ImageDraw, press: Press, r: float):
        (x, y) = self.calculate_xy_position(press)
        elt = self.select_string(press)
        font_size = clamp(int(self.scale / 4), 4, 32) * 4 # Only divisible by 4
        draw_context.text((x,y), 
            text=elt, 
            fill=(255, 0, 0), 
            anchor="mm",
            font=self.font_cache(font_size)
        )

class RandomWord(RandomText):
    DICTIONARY = get_dictionary("english5000.txt")  
    def select_string(self, press: Press) -> str:
        return RandomWord.DICTIONARY[hash(press) % len(self.DICTIONARY)]

class RandomJapaneseWord(RandomText):
    DICTIONARY = get_dictionary("japanese6000.txt")    
    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
        #self.font = get_font("sazanami-mincho.ttf", self.icon_size)
        #self.font = get_font("sazanami-gothic.ttf", self.icon_size)
        self.font_name = "HanaMinA.ttf"

    def select_string(self, press: Press) -> str:
        return RandomJapaneseWord.DICTIONARY[hash(press) % len(self.DICTIONARY)]

class RandomIcon(RandomText):
    SYMBOLS = [c for c in "★✶✢❤︎✕⨳♚♛♜♝♞♟♔♕♖♗♘♙♈︎♉︎♊︎♋︎♌︎♍︎♎︎♏︎♐︎♑︎♒︎♓︎☉☿♀︎♁♂︎♃♄♅♆⚕︎⚚☯︎⚘✦✧⚡︎"]
    def select_string(self, press: Press) -> str:
        index = hash(press) % len(self.SYMBOLS)
        return RandomIcon.SYMBOLS[index] + str(index)
    
    
class RandomNumber(RandomText):
    def select_string(self, press: Press) -> str:
        return str(hash(press) % 100)

