from dataclasses import dataclass
import logging
import time
from typing import Tuple
import numpy as np
import colorsys

log = logging.getLogger(__name__)


@dataclass
class Dimensions:
    width: int
    height: int
 
def clamp(x, lower, upper):
    if not lower <= x <= upper:
        log.warning(f"Input, {x}, outside of acceptable bounds of [{lower}, {upper}]")
        return min(upper, max(lower, x))
    return x

clamped_add = lambda x, y: min(1.0, x + y)
clamped_subtract = lambda x, y: max(0.0, x - y)

def hsv_to_pixel(h: float, s: float, v: float) -> Tuple[np.uint8,np.uint8,np.uint8]:
    rgb = colorsys.hsv_to_rgb(h, s, v)
    return (np.uint8(rgb[0] * 255), np.uint8(rgb[1] * 255), np.uint8(rgb[2] * 255))

def loopwait(t_last: float, max_dt: float):
    # Respecting max_dt, wait for up to 
    now = time.time()
    total_elapsed_since_last_frame = now - t_last
    t_last, wait_time = now, max_dt - total_elapsed_since_last_frame
    if wait_time < 0:
        log.debug(f"Frame dt exceeded: {wait_time}")
    else:
        time.sleep(wait_time)
    return now, total_elapsed_since_last_frame