#!/usr/bin/env python

from rgb.form.keyawareform import Press, KeyAwareForm
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


from rgb.constants import PAD_INDICES, NUM_NOTES
from rgb.utilities import clamp
from rgb.form.baseform import BaseForm

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))


@dataclass
class Elt:
    def __init__(self, x: float, y: float, vx: float, vy: float, hue: float):
        self.x: float = x
        self.y: float = y
        self.vx: float = vx
        self.vy: float = vy
        self.hue: float = hue

    def __str__(self):
        return json.dumps({key: getattr(self, key) for key in ["x", "y", "vx", "vy"]})

    def __hash__(self):
        return hash((self.x, self.y, self.hue))

    def __eq__(self, other):
        return hash(self) == hash(other)

    @property
    def rgb(self) -> Tuple[np.uint8, np.uint8, np.uint8]:
        rgb = colorsys.hsv_to_rgb(self.hue, 1.0, 1.0)
        return (np.uint8(rgb[0] * 255), np.uint8(rgb[1] * 255), np.uint8(rgb[2] * 255))


class Gravity(KeyAwareForm):

    # Shape := The bounds of the random.uniform x velocity
    MAX_SHAPE = 0.004  # Random.uniform [-0.004, 0.004] m/s

    # Add randomness to prevent grouping along horizontals
    JITTERS = 32

    def __init__(self, dimensions: Tuple[int, int], meters_per_pixel: float):
        super().__init__(dimensions)
        (self.matrix_width, self.matrix_height) = dimensions
        self.world_width = self.matrix_width * meters_per_pixel
        self.world_height = self.matrix_height * meters_per_pixel
        self.population = 484
        self.particles: Set[Elt] = set()
        self.jitters = [random.uniform(0.85, 1.15) for _ in range(Gravity.JITTERS)]

    @property
    def gravitational_constant(self) -> float:
        """
        Logarithmic scale timespan for dial

        State 0.0 := g = 0.05 m/s^2
        State 1.0 := g = 12 m/s^2
        """
        # math.exp(0) = 1.0
        # math.exp(2.5) = 12.18

        return -clamp(BaseForm.dials(2), 0.0, 1.0) * 10

    @property
    def shape(self) -> float:
        """
        Logarithmic scale timespan for dial

        State 0.0 := g = 0.05 m/s^2
        State 1.0 := g = 12 m/s^2
        """
        # math.exp(0) = 1.0
        # math.exp(2.5) = 12.18

        return clamp(BaseForm.dials(3), 0.0, 1.0) * Gravity.MAX_SHAPE

    def midi_handler(self, value: Dict):
        super().midi_handler(value)
        if value["type"] == "note_on" and value["note"] == PAD_INDICES[2]:
            self.population = max(self.population - 16, 0)
        elif value["type"] == "note_on" and value["note"] == PAD_INDICES[3]:
            self.population = min(self.population + 16, 512)
        
    def button_0_handler(self, state: bool):
        if state:
            self.population = min(self.population + 1, 512)

    def button_1_handler(self, state: bool):
        if state:
            self.population = max(self.population - 1, 0)

    @property
    def matrix_scale(self) -> float:
        # E.g. 1:4 would be 0.25
        return self.matrix_height / float(self.world_height)

    def _birth_particles(self):
        room = self.population - len(self.particles)
        if room <= 0:
            return
        births = random.randint(0, room) // 10
        for _ in range(int(births)):
            self.particles.add(
                Elt(
                    x=self.world_width / 2,
                    y=self.world_height,
                    vx=random.uniform(-self.shape, self.shape),
                    vy=0,
                    hue=random.random(),
                )
            )

    def step(self, dt: float):
        super().step(dt)
        self._birth_particles()

        for i, elt in enumerate(self.particles):
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
            elt.y = elt.y + (elt.vy * dt * self.jitters[i % Gravity.JITTERS])
        self.particles = set(filter(lambda x: x.y >= 0, self.particles))
        return self._render()

    def _render(self) -> Image.Image:
        img = np.zeros((self.matrix_height, self.matrix_width, 3), dtype=np.uint8)
        for elt in self.particles:

            render_y = round(self.matrix_scale * elt.y)
            render_x = round(self.matrix_scale * elt.x)

            if 0 <= render_y < self.matrix_height and 0 <= render_x < self.matrix_width:
                rgb = elt.rgb
                img[render_y, render_x, 0] = rgb[0]
                img[render_y, render_x, 1] = rgb[1]
                img[render_y, render_x, 2] = rgb[2]
            # Else, skip it
        # Return the vertical flip, origin at the top.
        return Image.fromarray(img).transpose(Image.FLIP_TOP_BOTTOM)


class GravityKeys(Gravity):
    def __init__(self, dimensions: Tuple[int, int], meters_per_pixel: float):
        super().__init__(dimensions, meters_per_pixel)

    def particle_from_keypress(self, key: Press) -> Elt:
        key_unit = key.note / NUM_NOTES
        return Elt(
            x=self.world_width / 2, y=self.world_height, vx=random.uniform(-self.shape, self.shape), vy=0, hue=key_unit
        )

    def _birth_particles(self):
        room = self.population - len(self.particles)
        if room <= 0:
            return
        births = random.randint(0, room) // 10
        for key in self.presses().values():
            for _ in range(int(births)):
                self.particles.add(self.particle_from_keypress(key))


class GravityKeysMultiNozzle(GravityKeys):
    def __init__(self, dimensions: Tuple[int, int], meters_per_pixel: float):
        super().__init__(dimensions, meters_per_pixel)

    def particle_from_keypress(self, key: Press) -> Elt:
        key_unit = key.note_index / NUM_NOTES
        launch_point = key_unit * self.world_width
        return Elt(x=launch_point, y=self.world_height, vx=random.uniform(-self.shape, self.shape), vy=0, hue=key_unit)
