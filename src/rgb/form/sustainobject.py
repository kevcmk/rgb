#!/usr/bin/env python

import colorsys
from rgb.utilities import clamp
from rgb.form.keyawareform import KeyAwareForm
from rgb.parameter_tuner import ParameterTuner
from rgb.form.transitions import transition_ease_in, transition_ease_out_exponential
from rgb.form.keyawareform import Press
from rgb.utilities import get_dictionary
from rgb.utilities import get_font
import logging
import math
import os
import time
from collections import OrderedDict
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple, Union
from rgb.constants import NUM_NOTES, NUM_PIANO_KEYBOARD_KEYS, MIDI_DIAL_MAX

import numpy as np
from rgb.form.baseform import BaseForm
from PIL import Image, ImageDraw, ImageFont
from rgb.utilities import is_key_press

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))

PRIME_FOR_HASH = 5021

class SimpleSustainObject(KeyAwareForm):

    MAX_ATTACK_TIME_S = 0.5
    MAX_RELEASE_TIME_S = 3.0

    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
        
        self.base_hue = 0.0
        
        self.presses: OrderedDict[int, Press] = OrderedDict()
        
        self.smallest_to_largest_note_base_ratio_min = 1.0
        self.smallest_to_largest_note_base_ratio_max = 10.0
        self.smallest_to_largest_note_base_ratio = 99.0 # Placeholder value
        self.set_smallest_to_largest_note_base_ratio(0.5)
        
        self.smallest_note_radius_min = 2.0
        self.smallest_note_radius_max = 10.0
        self.smallest_note_radius = 99.0 # Placeholder value
        self.set_smallest_note_radius(0.5)
        
        self.maximum_grow_velocity_per_s = 10.0
        
        # The logarithmic base of the size of a shape. High notes are smaller than low notes, a low base means the differences between high and low notes are more apparent.
        self.attack_time_s_min = 0.0
        self.attack_time_s_max = 0.0
        self.attack_time_s = 99.0 # Placeholder value
        self.set_attack_time_s(0.0)
        
        self.release_time_s_min = 0.0
        self.release_time_s_max = 0.5
        self.release_time_s = 99.0 
        self.set_release_time_s(0.1)
    
    """
    Size / Growth
    """
    def set_smallest_note_radius(self, value: float) -> float:
        self.smallest_note_radius = ParameterTuner.linear_scale(value, minimum=self.smallest_note_radius_min, maximum=self.smallest_note_radius_max)
        return self.smallest_note_radius

    def set_smallest_to_largest_note_base_ratio(self, value: float) -> float:
        self.smallest_to_largest_note_base_ratio = ParameterTuner.linear_scale(value, minimum=self.smallest_to_largest_note_base_ratio_min, maximum=self.smallest_to_largest_note_base_ratio_max)
        return self.smallest_to_largest_note_base_ratio

    def calculate_grow_velocity_per_s(self, p: Press) -> float:
        note_unit = p.note / NUM_PIANO_KEYBOARD_KEYS
        return ParameterTuner.linear_scale(v=note_unit, minimum=0.0, maximum=self.maximum_grow_velocity_per_s)

    def calculate_radius(self, p: Press, current_time: float) -> float:
        # If released, stop growing
        dt = p._t_released - p.t if p._t_released else current_time - p.t 
        note = p.note
        note_unit = (109 - note) / 109  # A [0-1) number
        base_radius = ParameterTuner.exponential_scale(v=note_unit, exponent=0.5, minimum=self.smallest_note_radius, maximum=self.smallest_note_radius * self.smallest_to_largest_note_base_ratio)
        return base_radius + dt * self.calculate_grow_velocity_per_s(p)

    """
    Color
    """
    def calculate_hue(self, p: Press) -> float:
        """
        This default hue calculation is based on the octave-periodic note value. Returns a [0,1] value.
        """
        note_unit = (p.note % NUM_NOTES) / NUM_NOTES
        return (self.base_hue + note_unit) % 1.0

    def calculate_color(self, p: Press) -> Tuple[int, int, int, int]:
        """
        Default color calculation. Returns an RGBA [0,255] value based on the note value.
        """
        dt = time.time() - p.t    
        alpha = self.compute_envelope(dt, p._t_released)
        hue = self.calculate_hue(p)
        rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        return (int(255 * rgb[0]), int(255 * rgb[1]), int(255 * rgb[2]), int(255 * alpha))
    
    """
    Transition
    """

    def set_attack_time_s(self, value: float) -> float:
        self.attack_time_s = ParameterTuner.linear_scale(value, minimum=self.attack_time_s_min, maximum=self.attack_time_s_max)
        return self.attack_time_s

    def set_release_time_s(self, value: float) -> float:
        self.release_time_s = ParameterTuner.linear_scale(value, minimum=self.release_time_s_min, maximum=self.release_time_s_max)
        return self.release_time_s

    def compute_envelope(self, dt: float, t_released: Optional[float]) -> float:
        x = transition_ease_in(dt / self.attack_time_s) if self.attack_time_s != 0 else 1.0
         
        if t_released is None:
            return x
        else:
            time_since_release = time.time() - t_released
            if self.release_time_s != 0:
                decay = 1 - transition_ease_out_exponential(time_since_release / self.release_time_s, exponent=5)
            else:
                decay = 0.0
            return decay * x

    """
    Position
    """
    def calculate_xy_fractional_position(self, p: Press) -> Tuple[float, float]:
        # Return the floating point fractional [0,1] within the matrix width and height
        position_x = (hash(p.t) % PRIME_FOR_HASH) / PRIME_FOR_HASH
        position_y = (hash(p.t * 2) % PRIME_FOR_HASH) / PRIME_FOR_HASH
        return (position_x, position_y)
    
    def calculate_xy_position(self, p: Press) -> Tuple[int, int]:
        fractional_x, fractional_y = self.calculate_xy_fractional_position(p)
        return (int(fractional_x * self.matrix_width), int(fractional_y * self.matrix_height))

    def midi_handler(self, value: Dict):
        super().midi_handler(value)
        # Key Press: msg.dict() -> {'type': 'note_on', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0} {'type': 'note_off', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0}
        
        if value['type'] == 'control_change' and value['control'] == 14:
            self.smallest_note_radius = self.set_smallest_note_radius(value['value'] / MIDI_DIAL_MAX)
        elif value['type'] == 'control_change' and value['control'] == 15: 
            self.grow_velocity = value['value'] / 4
            log.debug('Grow: {self.grow}')
        elif value['type'] == 'control_change' and value['control'] == 16:
            self.set_attack_time_s(value['value'] / MIDI_DIAL_MAX)
            self.set_release_time_s(value['value'] / MIDI_DIAL_MAX)
        elif value['type'] == 'control_change' and value['control'] == 17: 
            pass
            log.debug('Grow Ratio: {self.grow_ratio}')

    def step(self, dt: float) -> Union[Image.Image, np.ndarray]:
        super().step(dt) # Ignore super's return value, it's not relevant.
        img = Image.new("RGB", (self.matrix_width, self.matrix_height), (0, 0, 0)) 
        
        # For whatever reason, to do transparent shapes, we use RGBA draw_context over RGB image
        # https://stackoverflow.com/a/21768191
        draw_context = ImageDraw.Draw(img, "RGBA")
        now = time.time()
        for press in self.presses.values():
            r = self.calculate_radius(press, current_time=now)
            self.draw_shape(draw_context, press, r)
        del draw_context
        
        return img

    @abstractmethod
    def draw_shape(self, draw_context, press: Press, r: float):
        pass

class VerticalNotes(SimpleSustainObject):
    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
        # 0 until 1 before matrix_width, num keys + 1 steps (because we index [i,i+1]
        self.x_coords = np.linspace(0, self.matrix_width, NUM_NOTES + 1, dtype=np.uint8)

    def draw_shape(self, draw_context: ImageDraw.ImageDraw, press: Press, r: float):
        color = self.calculate_color(press)
        lo = self.x_coords[press.note % NUM_NOTES]
        hi = self.x_coords[press.note % NUM_NOTES + 1] - 1
        draw_context.rectangle((lo, 0, hi, self.matrix_height), fill=color)

class VerticalWaves(VerticalNotes):
    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
        # 0 until 1 before matrix_width, num keys + 1 steps (because we index [i,i+1]
        self.x_coords = np.linspace(0, self.matrix_width, NUM_NOTES + 1, dtype=np.uint8)
        self.wave_width = 4

    @staticmethod
    def modulate_alpha(c: Tuple[int, int, int, int], factor: float) -> Tuple[int, int, int, int]:
        return (c[0], c[1], c[2], clamp(int(factor * c[3]), 0, 255))

    def draw_shape(self, draw_context: ImageDraw.ImageDraw, press: Press, r: float):
        color = self.calculate_color(press)
        lo = self.x_coords[press.note % NUM_NOTES]
        hi = self.x_coords[press.note % NUM_NOTES + 1] - 1
        draw_context.rectangle((lo, 0, hi, self.matrix_height), fill=color)
        # print(r // 8)
        max_wave_width = int(r / 4)
        for i in range(max_wave_width):
            # Don't worry, this works. Tuple4 is acceptable.
            scale = ParameterTuner.exponential_scale((i+1) / max_wave_width, 0.5, 1.0, 0.0)
            print(scale)
            if 0 <= lo - i < self.matrix_width:
                draw_context.rectangle((lo - i , 0, lo - i, self.matrix_height), fill=VerticalWaves.modulate_alpha(color, scale))
            if 0 <= hi + i < self.matrix_width:
                draw_context.rectangle((hi + i, 0, hi + i, self.matrix_height), fill=VerticalWaves.modulate_alpha(color, scale))

class VerticalNotesFullSpectrum(VerticalNotes):
    def calculate_hue(self, p: Press) -> float:
        note_unit = p.note / NUM_PIANO_KEYBOARD_KEYS
        return (self.base_hue + note_unit) % 1.0

class VerticalKeys(SimpleSustainObject):
    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
        # 0 until 1 before matrix_width, num keys + 1 steps (because we index [i,i+1]
        self.x_coords = np.linspace(0, self.matrix_width, NUM_PIANO_KEYBOARD_KEYS + 1, dtype=np.uint8)
    
    def draw_shape(self, draw_context: ImageDraw.ImageDraw, press: Press, r: float):
        color = self.calculate_color(press)
        lo = self.x_coords[press.note]
        # If co-vertical, the -1 produces an x less than lo, thus the column can be though of as a single [lo,lo]

        hi = max(lo, self.x_coords[press.note + 1] - 1)
        draw_context.rectangle((lo, 0, hi, self.matrix_height), fill=color)

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

class RandomSolidShapeFullSpectrum(RandomSolidShape):
    def calculate_hue(self, p: Press) -> float:
        return p.note / NUM_PIANO_KEYBOARD_KEYS
     
class RandomSolidShapeFullSpectrumWithEvolvingHue(RandomSolidShape):
    HUE_INCREMENT = 0.05
    def midi_handler(self, value: Dict):
        if is_key_press(value):
            self.base_hue = (self.base_hue + RandomSolidShapeFullSpectrumWithEvolvingHue.HUE_INCREMENT) % 1.0
        return super().midi_handler(value)
        

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
        color = self.calculate_color(press)
        # TODO Alpha doesn't work here.
        draw_context.text((x,y), 
            text=elt, 
            fill=color, 
            anchor="mm",
            font=self.font_cache(int(r))
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
        return RandomIcon.SYMBOLS[index]

    
    
    
class RandomNumber(RandomText):
    def select_string(self, press: Press) -> str:
        return str(hash(press) % 100)

