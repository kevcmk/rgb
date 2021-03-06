#!/usr/bin/env python

import datetime
from rgb.utilities import get_font
import logging
import os
from dataclasses import dataclass
from random import randrange
from typing import Dict, List, Optional, Set, Tuple

import numpy as np

from PIL import Image, ImageDraw, ImageFont
from rgb.form.baseform import BaseForm

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))

class Timer(BaseForm):
    def __init__(self, dimensions: Tuple[int, int]):
        self.max_hz = 60
        (self.matrix_width, self.matrix_height) = dimensions
        self.t_stop: Optional[datetime.datetime] = None
        self.font = get_font("DejaVuSans.ttf", 14)
        self.enable_visual = True

        self.handlers = {
            "Switch": {
                0: self.switch_handler,
            },
            "Button": {
                0: self.button_0_handler,
                1: self.button_1_handler
            }
        }
    
    def switch_handler(self, state: bool):
        self.enable_visual = state
    
    def button_0_handler(self, state: bool):
        if state:
            self.t_stop = None

    def button_1_handler(self, state: bool):
        if state:
            self.t_stop = (self.t_stop or datetime.datetime.now()) + datetime.timedelta(minutes=1)

    @staticmethod
    def render_dt(dt: datetime.timedelta) -> str:
        return str(f"{int(dt.seconds / 60)}:{dt.seconds % 60:02}")

    def _render(self) -> Image.Image:
        im = Image.new("RGB", (self.matrix_width, self.matrix_height))
        draw_context = ImageDraw.Draw(im)
        log.debug(f"t_stop {self.t_stop}")
        if self.t_stop is not None:
            now = datetime.datetime.utcnow()
            if self.t_stop < now:
                if now - self.t_stop < datetime.timedelta(minutes=1):
                    color = (255, 165, 0)
                else:
                    color = (255, 0, 0)
                draw_context.rectangle([(0,0),im.size], fill = color)
            else:
                dt_text = Timer.render_dt(self.t_stop - now)
                draw_context.text((16,16), 
                    text=dt_text, 
                    fill=(255, 0, 0), 
                    anchor="mm",
                    font=self.font
                )
        return im.transpose(Image.FLIP_TOP_BOTTOM)

    def step(self, dt: float):
        return self._render()

    
       
