#!/usr/bin/env python

import random
import json
from typing import List, Set, Tuple
import math
from random import randrange
import time
import numpy as np
from PIL import Image
from dataclasses import dataclass
import colorsys
from typing import Dict
from rgb.form.baseform import BaseForm


class Chase(BaseForm):
    def __init__(self, height: int):
        self.index = 0
        self.height = height

    def step(self, dt: float):
        mat = np.zeros((self.height, 3))
        mat[(self.index - 0) % self.height, :] = (np.uint8(255), np.uint8(0), np.uint8(0))
        mat[(self.index - 1) % self.height, :] = (np.uint8(127), np.uint8(0), np.uint8(0))
        mat[(self.index - 2) % self.height, :] = (np.uint8(63), np.uint8(0), np.uint8(0))
        mat[(self.index - 3) % self.height, :] = (np.uint8(31), np.uint8(0), np.uint8(0))
        mat[(self.index - 4) % self.height, :] = (np.uint8(15), np.uint8(0), np.uint8(0))
        mat[(self.index - 4) % self.height, :] = (np.uint8(7), np.uint8(0), np.uint8(0))
        mat[(self.index - 5) % self.height, :] = (np.uint8(3), np.uint8(0), np.uint8(0))
        mat[(self.index - 6) % self.height, :] = (np.uint8(1), np.uint8(0), np.uint8(0))
        mat[(self.index - 7) % self.height, :] = (np.uint8(0), np.uint8(0), np.uint8(0))
        self.index += 1
        return mat
