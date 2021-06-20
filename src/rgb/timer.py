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
from random import randrange
from typing import List, Set, Tuple, Optional

import numpy as np
import numpy.typing as npt
from PIL import Image, ImageDraw, ImageFont

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))

class Timer():
    def __init__(self, matrix_height: int, matrix_width: int):
        self.hz = 60
        self.matrix_height = matrix_height
        self.matrix_width = matrix_width
        self.t_stop: Optional[datetime.datetime] = None
        self.font = ImageFont.truetype("rgb/DejaVuSans.ttf", 14)
        self.enable_visual = True
    
    @staticmethod
    def render_dt(dt: datetime.timedelta) -> str:
        return str(f"{int(dt.seconds / 60)}:{dt.seconds % 60:02}")

    def _render(self) -> Image.Image:
        im = Image.new("RGB", (self.matrix_width, self.matrix_height))
        draw_context = ImageDraw.Draw(im)
        log.debug(f"t_stop {self.t_stop}, enable_visual: {self.enable_visual}")
        if self.t_stop is not None and self.enable_visual:
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
        return im

    def step(self, dt) -> Image.Image:
        return self._render()

    
       


# Main function
if __name__ == "__main__":
    gravity = Gravity()
    if not gravity.process():
        gravity.print_help()

