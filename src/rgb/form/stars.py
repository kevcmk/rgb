#!/usr/bin/env python

import random
import json
from typing import List, Set, Tuple
import math
from random import randrange
import time
import numpy as np
from dataclasses import dataclass
import colorsys
from typing import Dict
from PIL import Image
from rgb.form.baseform import BaseForm


@dataclass
class Elt:
    def __init__(self):
        self.x: float = random.random()
        self.y: float = random.random()
        self.hue: float = random.random()
        self.born: float = time.time()
        self.lifespan: float = 10 * random.random()
    
    def __str__(self):
        return json.dumps({key: getattr(self, key) for key in ["x","y","hue","born","lifespan","age", "alive", "luminance"]})

    def __hash__(self):
        return hash((self.x, self.y, self.hue))
    
    def __eq__(self, other):
        return hash(self) == hash(other)

    @property
    def age(self) -> float:
        return time.time() - self.born
    
    @property
    def alive(self) -> bool:
        return self.age <= self.lifespan

    @property
    def luminance(self):
        return self.age / self.lifespan
        #sqr = self.age ** 2
        #t = self.age / self.lifespan
        #res = sqr / (2.0 * (sqr - t) + 1.0)
        #return min(1.0, res * 2)
        
    
class Stars(BaseForm):
    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
        self.population = 256
        self.elts: Set[Elt] = {Elt() for _ in range(self.population)}
        self.handlers = {}
    
    def midi_handler(self, value: Dict):
        # TODO
        pass

    def step(self, dt: float):
        self.elts = set(filter(lambda x: x.alive, self.elts))
        self.elts.update([Elt() for _ in range(self.population - len(self.elts))])
        return self._render()      
        
    def _render(self):
        img = np.zeros((self.matrix_height, self.matrix_width, 3), dtype=np.uint8)
        for elt in self.elts:
            if elt.alive:
                rgb = colorsys.hsv_to_rgb(elt.hue, 1.0, elt.luminance) 
                render_y = round(self.matrix_height * elt.y)
                render_x = round(self.matrix_width * elt.x)
                if 0 <= render_y < self.matrix_height and \
                    0 <= render_x < self.matrix_width:
                    img[render_y,render_x,:] = (np.uint8(255 * rgb[0]), np.uint8(255 * rgb[1]), np.uint8(255 * rgb[2]))
        return Image.fromarray(img)