#!/usr/bin/env python

import colorsys
import logging
import os
import time
from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple, Union

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from rgb.constants import NUM_NOTES, NUM_PIANO_KEYBOARD_KEYS
from rgb.form.baseform import BaseForm
from rgb.form.keyawareform import KeyAwareForm, Press
from rgb.form.transitions import transition_ease_out_exponential
from rgb.parameter_tuner import ParameterTuner
from rgb.utilities import get_dictionary, get_font, modulate_alpha

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))

PRIME_FOR_HASH = 5021


def compute_envelope(dt: float, dt_released: Optional[float], attack_time_s: float, release_time_s: float) -> float:
    # Ease out exponential 3 on attack means aggressive entrance (60% after 0.25, 85% after 0.5)
    x = transition_ease_out_exponential(dt / attack_time_s, exponent=6) if attack_time_s != 0 else 1.0

    if dt_released is None:
        return x
    else:
        time_since_release = dt_released
        if release_time_s != 0:
            decay = 1 - transition_ease_out_exponential(time_since_release / release_time_s, exponent=5)
        else:
            decay = 0.0
        return decay * x


class SimpleSustainObject(KeyAwareForm):

    # Hues stepped from 0-1 in 12 steps, providing clear (255,127,0)-typed colors
    PIECEWISE_HUES = np.linspace(0, 1, num=NUM_NOTES, endpoint=False)

    MAX_ATTACK_TIME_S = 0.5
    MAX_RELEASE_TIME_S = 3.0

    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)

    """
    Size / Growth
    """

    @property
    def base_hue(self) -> float:
        # Why + 0.5 % 1.0 ? So we default rojo for dial 0.5.
        return ParameterTuner.linear_scale(BaseForm.dials(0), minimum=0, maximum=1.0)

    @property
    def attack_time_s(self) -> float:
        # return ParameterTuner.linear_scale(BaseForm.dials(1), minimum=0.0, maximum=0.1)
        return 0.0

    @property
    def smallest_note_radius(self) -> float:
        return ParameterTuner.linear_scale(BaseForm.dials(1), minimum=6, maximum=128)

    @property
    def release_time_s(self) -> float:
        return ParameterTuner.linear_scale(BaseForm.dials(2), minimum=0.0, maximum=0.5)

    @property
    def maximum_grow_velocity_per_s(self) -> float:
        # return ParameterTuner.linear_scale(BaseForm.dials(1), minimum=0, maximum=10.0)
        return 5.0

    @property
    def smallest_to_largest_note_base_ratio(self) -> float:
        # return ParameterTuner.linear_scale(BaseForm.dials(2), minimum=1.0, maximum=10.0)
        return 4.0

    def calculate_grow_velocity_per_s(self, p: Press) -> float:
        note_unit = p.note / NUM_PIANO_KEYBOARD_KEYS
        return ParameterTuner.linear_scale(v=note_unit, minimum=0.0, maximum=self.maximum_grow_velocity_per_s)

    def calculate_radius(self, p: Press, current_time: float) -> float:
        # If released, stop growing
        dt = p._t_released - p.t if p._t_released else current_time - p.t
        note = p.note
        note_unit = (109 - note) / 109  # A [0-1) number
        base_radius = ParameterTuner.exponential_scale(
            v=note_unit,
            exponent=0.5,
            minimum=self.smallest_note_radius,
            maximum=self.smallest_note_radius * self.smallest_to_largest_note_base_ratio,
        )
        return base_radius + dt * self.calculate_grow_velocity_per_s(p)

    """
    Color
    """

    def calculate_hue(self, p: Press) -> float:
        """
        This default hue calculation is based on the octave-periodic note value.
        Returns a stepwise-[0,1] value. Shifted by base_hue for picky synesthetics.
        """
        note_index = (p.note + int(self.base_hue * NUM_NOTES)) % NUM_NOTES
        return SimpleSustainObject.PIECEWISE_HUES[note_index]

    def calculate_color(self, p: Press) -> Tuple[int, int, int, int]:
        """
        Default color calculation. Returns an RGBA [0,255] value based on the note value.
        """
        dt = time.time() - p.t
        dt_released = time.time() - p._t_released if p._t_released else None
        alpha = compute_envelope(dt, dt_released, self.attack_time_s, self.release_time_s)
        hue = self.calculate_hue(p)
        rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        return (
            int(255 * rgb[0]),
            int(255 * rgb[1]),
            int(255 * rgb[2]),
            int(255 * alpha),
        )

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
        return (
            int(fractional_x * self.matrix_width),
            int(fractional_y * self.matrix_height),
        )

    def step(self, dt: float) -> Union[Image.Image, np.ndarray]:
        super().step(dt)  # Ignore super's return value, it's not relevant.
        img = Image.new("RGB", (self.matrix_width, self.matrix_height), (0, 0, 0))

        # For whatever reason, to do transparent shapes, we use RGBA draw_context over RGB image
        # https://stackoverflow.com/a/21768191
        draw_context = ImageDraw.Draw(img, "RGBA")
        now = time.time()
        for press in self.presses().values():
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
        # 0 until 1 before matrix_width, num keys + 1 steps (because we index [i,i+1])
        self.x_coords = np.linspace(0, self.matrix_width, NUM_NOTES + 1, dtype=np.uint8)

    def draw_shape(self, draw_context: ImageDraw.ImageDraw, press: Press, r: float):
        color = self.calculate_color(press)
        lo = self.x_coords[press.note % NUM_NOTES]
        hi = self.x_coords[press.note % NUM_NOTES + 1] - 1
        draw_context.rectangle((lo, 0, hi, self.matrix_height), fill=color)


class WaveSustainObject(SimpleSustainObject, ABC):
    # This must be mixed in to a concrete SimpleSustainObject

    @property
    def max_wave_width(self) -> int:
        return int(self.matrix_width * BaseForm.dials(2))

    @property
    def wave_attack_time(self) -> float:
        # Wave attack time is a fraction of the shape's attack time
        return BaseForm.dials(4) * self.attack_time_s

    @property
    def wave_release_time(self) -> float:
        # Wave Release time is a fraction of the shape's attack time
        return BaseForm.dials(5) * self.release_time_s

    def wave_scale(self, i, dt: float, dt_released: Optional[float]):
        compute_envelope(dt, dt_released, self.wave_attack_time, self.wave_release_time)
        return ParameterTuner.exponential_scale(i / self.max_wave_width, 0.5, 1.0, 0.0)


class RandomWaveShape(WaveSustainObject):
    def calculate_radius(self, p: Press, current_time: float) -> float:
        return super().calculate_radius(p, current_time) / 2

    @property
    def wave_step(self) -> float:
        d = BaseForm.dials(6)
        cutoff = 0.55
        if d < cutoff:
            return 1
        else:
            shifted = (d - cutoff) / (1 - cutoff)  # Convert [0.55, 1.0] -> [0.0, 1.0]
            return ParameterTuner.linear_scale(shifted, 1.0, 4.0)

    def draw_shape(self, draw_context: ImageDraw.ImageDraw, press: Press, r: float):
        (x, y) = self.calculate_xy_position(press)
        color = self.calculate_color(press)
        num_sides = int(((press.t * 100) % 5) + 3)
        rotation = ((press.t * 1000) % 1000) * 360

        dt = time.time() - press.t
        dt_released = time.time() - press._t_released if press._t_released else None

        for i in np.linspace(
            start=0, stop=self.max_wave_width, num=int(self.max_wave_width / self.wave_step), endpoint=False
        ):
            # Don't worry, this works. Tuple4 is acceptable.
            scale = self.wave_scale(i=i, dt=dt, dt_released=dt_released)
            draw_context.regular_polygon(
                (x, y, r + i), num_sides, rotation=rotation, fill=modulate_alpha(color, scale), outline=None
            )


class RandomWaveShapeReverseSlow(RandomWaveShape):
    def calculate_hue(self, p: Press) -> float:
        note_unit = p.note / NUM_PIANO_KEYBOARD_KEYS
        return -(self.base_hue + note_unit) % 1.0


class VerticalWaves(WaveSustainObject):
    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
        # 0 until 1 before matrix_width, num keys + 1 steps (because we index [i,i+1]
        self.x_coords = np.linspace(0, self.matrix_width, NUM_NOTES + 1, dtype=np.uint8)

    def draw_shape(self, draw_context: ImageDraw.ImageDraw, press: Press, r: float):
        color = self.calculate_color(press)
        lo = self.x_coords[press.note % NUM_NOTES]
        hi = self.x_coords[press.note % NUM_NOTES + 1] - 1
        # draw_context.rectangle((lo, 0, hi, self.matrix_height), fill=color)

        dt = time.time() - press.t
        dt_released = time.time() - press._t_released if press._t_released else None

        draw_context.rectangle(
            (lo, 0, hi, self.matrix_height),
            fill=color,  # Don't worry, this works. Tuple4 is acceptable.
        )
        for i in range(self.max_wave_width):
            scale = self.wave_scale(i, dt=dt, dt_released=dt_released)

            if 0 <= lo - i < self.matrix_width:
                draw_context.rectangle(
                    (lo - i, 0, lo - i, self.matrix_height),
                    fill=modulate_alpha(color, scale),  # Don't worry, this works. Tuple4 is acceptable.
                )
            if 0 <= hi + i < self.matrix_width:
                draw_context.rectangle(
                    (hi + i, 0, hi + i, self.matrix_height),
                    fill=modulate_alpha(color, scale),  # Don't worry, this works. Tuple4 is acceptable.
                )


class RandomVerticalWaveReverseSlow(VerticalWaves):
    def calculate_hue(self, p: Press) -> float:
        note_unit = p.note / NUM_PIANO_KEYBOARD_KEYS
        return -(self.base_hue + note_unit) % 1.0


class RandomVerticalWaveReverseSlowDarkerLows(RandomVerticalWaveReverseSlow):
    def calculate_color(self, p: Press) -> Tuple[int, int, int, int]:
        c = super().calculate_color(p)
        return modulate_alpha(c, ParameterTuner.linear_scale(p.note / float(NUM_NOTES), BaseForm.dials(7), 1.0))


class RandomVerticalWaveReverseSlowDarkerLowsRed(RandomVerticalWaveReverseSlowDarkerLows):
    def calculate_hue(self, p: Press) -> float:
        note_unit = p.note / NUM_PIANO_KEYBOARD_KEYS
        return ParameterTuner.linear_scale(note_unit, 0, 0.125 + 0.08) - 0.08


class VerticalNotesSlowSpectrum(VerticalWaves):
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


class RandomSolidShapeSlowSpectrum(RandomSolidShape):
    def calculate_hue(self, p: Press) -> float:
        note_unit = p.note / NUM_PIANO_KEYBOARD_KEYS
        return (self.base_hue + note_unit) % 1.0


class RandomText(SimpleSustainObject):
    # TODO Make abstract?
    def select_string(self, press: Press) -> str:
        raise NotImplementedError

    def calculate_radius(self, p: Press, current_time: float) -> float:
        return int(super().calculate_radius(p, current_time))

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

    def calculate_hue(self, p: Press) -> float:
        return self.base_hue  # Use base hue

    def calculate_grow_velocity_per_s(self, p: Press) -> float:
        return 0.0  # Don't grow

    def draw_shape(self, draw_context: ImageDraw.ImageDraw, press: Press, r: float):
        (x, y) = self.calculate_xy_position(press)
        elt = self.select_string(press)
        color = self.calculate_color(press)
        # TODO Alpha doesn't work here.
        draw_context.text((x, y), text=elt, fill=color, anchor="mm", font=self.font_cache(int(r)))


class RandomWord(RandomText):
    DICTIONARY = get_dictionary("english5000.txt")

    def select_string(self, press: Press) -> str:
        return RandomWord.DICTIONARY[hash(press) % len(self.DICTIONARY)]


class RandomJapaneseWord(RandomText):
    DICTIONARY = get_dictionary("japanese6000.txt")

    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
        # self.font = get_font("sazanami-mincho.ttf", self.icon_size)
        # self.font = get_font("sazanami-gothic.ttf", self.icon_size)
        self.font_name = "HanaMinA.ttf"

    def select_string(self, press: Press) -> str:
        return RandomJapaneseWord.DICTIONARY[hash(press) % len(self.DICTIONARY)]


class RandomIcon(RandomText):
    random = "★☆※ɵӿ†⁂⁃⁙⁜∮∧∨⋇⋆⌬☀⚕︎⚚☯︎⚘✦✧Ɣжѻ"
    planets = "☿♀♁♂♃♄♅♆♇"
    horoscope = "♈♉♊♋♌♍♎♏♐♑♒♓"
    cards = "♠♤♥♡♣♧♦♢"
    SYMBOLS = [c for c in random + planets + horoscope + cards]

    # "𐌊𐌄𐌞𐌉𐌍 𐌊𐌀𐌕"

    def select_string(self, press: Press) -> str:
        index = hash(press) % len(RandomIcon.SYMBOLS)
        return RandomIcon.SYMBOLS[index]
        # return RandomIcon.random


class TextSparkles(RandomText):
    def select_string(self, press: Press) -> str:
        return "✦"


class TextStars(RandomText):
    SYMBOLS = "★☆"

    def select_string(self, press: Press) -> str:
        return TextStars.SYMBOLS[hash(press) % len(self.SYMBOLS)]


class RandomNumber(RandomText):
    def select_string(self, press: Press) -> str:
        return str(hash(press) % 100)
