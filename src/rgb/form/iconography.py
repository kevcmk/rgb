#!/usr/bin/env python

import colorsys
import datetime
import json
import logging
import math
import os
import random
import time
from dataclasses import dataclass
from random import randint, randrange
from typing import Dict, List, Optional, Set, Tuple

import numpy as np

from PIL import Image, ImageDraw, ImageFont
from rgb.form.baseform import BaseForm
from rgb.utilities import get_font

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))

class Iconography(BaseForm):
    def __init__(self, dimensions: Tuple[int, int]):
        self.max_hz = 60
        (self.matrix_width, self.matrix_height) = dimensions
        self.icon_size = 18
        self.font = get_font("DejaVuSans.ttf", self.icon_size)
        # self.palette = "⤬⤯★✶✢❤︎✕⨳⩕⩙♚♛♜♝♞♟♔♕♖♗♘♙♈︎♉︎♊︎♋︎♌︎♍︎♎︎♏︎♐︎♑︎♒︎♓︎☉☿♀︎♁♂︎♃♄♅♆⚕︎⚚☯︎⚘✦✧⚡︎"
        self.palette = "𓃠𓃡𓃢𓃣𓃤𓃥𓃦𓃧𓃨𓃩𓃪𓃫𓃬𓃭𓃮𓃯𓀠𓀡𓀢𓀣𓀤𓀥𓀦"
        
    def _render(self) -> Image.Image:
        im = Image.new("RGB", (self.matrix_width, self.matrix_height))
        draw_context = ImageDraw.Draw(im)
        # TODO Get correct sampler
        text = self.palette[random.randint(0, len(self.palette) - 1)]
        x = random.randint(0, self.matrix_width)
        y = random.randint(0, self.matrix_height)
        draw_context.text((x,y), 
            text=text, 
            fill=(255, 0, 0), 
            anchor="mm",
            font=self.font
        )
        return im

    def step(self, dt: float):
        return self._render()

