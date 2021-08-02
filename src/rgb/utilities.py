from dataclasses import dataclass
from rgb.constants import PAD_INDICES, DIAL_INDICES
import logging
import time
from typing import Dict, List, Tuple
from PIL import ImageFont
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

RESOURCE_PATHS = ["src/rgb/resources/", "rgb/resources/"]
def get_dictionary(name: str) -> List[str]:
    for base in RESOURCE_PATHS:
        path = f"{base}{name}"
        try:
            with open(path, 'r') as f:
                return f.readlines()
        except OSError:
            log.debug(f"Could not open {path}, skipping...")
    raise ValueError(f"Could not find {name} in {RESOURCE_PATHS}")

def get_font(font, font_size: int):
    
    for base in RESOURCE_PATHS:
        path = f"{base}{font}"
        try:
            return ImageFont.truetype(path, font_size)
        except OSError:
            log.debug(f"Could not open {path}, skipping...")
    raise ValueError(f"Could not find font {font} in {RESOURCE_PATHS}")


def pad(index: int, m: Dict) -> bool:
    return m['type'] == 'note_on' and m.get('note', None) == PAD_INDICES[index]

def dial(index: int, m: Dict) -> bool:
    return m['type'] == 'control_change' and m.get('control', None) == DIAL_INDICES[index]

def sustain_on(m: Dict) -> bool:
    return m['type'] == 'control_change' and m.get('control', None) == 64 and m.get('value', None) == 127 and m.get("channel", None) == 0

def sustain_off(m: Dict) -> bool:
    return m['type'] == 'control_change' and m.get('control', None) == 64 and m.get('value', None) == 0 and m.get("channel", None) == 0


"""
# Press
2021-07-28T11:05:54-0700 vmini {"type": "control_change", "time": 0, "control": 64, "value": 127, "channel": 0, "midi_read_time": "2021-07-28 18:05:55.155991"} <------------ Press
2021-07-28T11:05:54-0700 vmini {"type": "control_change", "time": 0, "control": 64, "value": 0, "channel": 1, "midi_read_time": "2021-07-28 18:05:55.157802"}
2021-07-28T11:05:54-0700 vmini {"type": "control_change", "time": 0, "control": 64, "value": 127, "channel": 2, "midi_read_time": "2021-07-28 18:05:55.159192"}
2021-07-28T11:05:54-0700 vmini {"type": "sysex", "time": 0, "data": [0, 32, 84, 38, 9, 0, 127], "midi_read_time": "2021-07-28 18:05:55.161117"}
2021-07-28T11:05:54-0700 vmini {"type": "sysex", "time": 0, "data": [0, 32, 84, 38, 9, 1, 127], "midi_read_time": "2021-07-28 18:05:55.162283"}
2021-07-28T11:05:54-0700 vmini {"type": "sysex", "time": 0, "data": [0, 32, 84, 38, 9, 2, 127], "midi_read_time": "2021-07-28 18:05:55.163747"}
# Release
2021-07-28T11:05:57-0700 vmini {"type": "control_change", "time": 0, "control": 64, "value": 0, "channel": 0, "midi_read_time": "2021-07-28 18:05:58.269462"} <------------ Release
2021-07-28T11:05:57-0700 vmini {"type": "control_change", "time": 0, "control": 64, "value": 0, "channel": 1, "midi_read_time": "2021-07-28 18:05:58.272720"}
2021-07-28T11:05:57-0700 vmini {"type": "control_change", "time": 0, "control": 64, "value": 0, "channel": 2, "midi_read_time": "2021-07-28 18:05:58.274453"}
2021-07-28T11:05:57-0700 vmini {"type": "sysex", "time": 0, "data": [0, 32, 84, 38, 9, 0, 0], "midi_read_time": "2021-07-28 18:05:58.276304"}
2021-07-28T11:05:57-0700 vmini {"type": "sysex", "time": 0, "data": [0, 32, 84, 38, 9, 1, 0], "midi_read_time": "2021-07-28 18:05:58.279284"}
2021-07-28T11:05:57-0700 vmini {"type": "sysex", "time": 0, "data": [0, 32, 84, 38, 9, 2, 0], "midi_read_time": "2021-07-28 18:05:58.280181"}
"""


