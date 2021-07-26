#!/usr/bin/env python

from abc import abstractproperty
import colorsys
import json
import logging
import math
import os
import random
import time
from dataclasses import dataclass
from random import randrange
from typing import Dict, List, Set, Tuple
import datetime
from constants import NUM_NOTES, MIDI_DIAL_MAX

import numpy as np
import numpy.typing as npt
from PIL import Image
from rgb.form.baseform import BaseForm

from rgb.messages import Dial
from rgb.utilities import clamp

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))

@dataclass
class Press():
    t: float
    note: int
    velocity: int

class KeyAwareForm(BaseForm):
    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
        self.presses = dict()

    def cleanup(self):
        self.presses = dict()
    
    def midi_handler(self, value: Dict):
        # Key Press: msg.dict() -> {'type': 'note_on', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0} {'type': 'note_off', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0}
        if value['type'] == 'note_on':
            note = value['note']
            velocity = value['velocity'] / MIDI_DIAL_MAX
            self.presses[note] = Press(t=time.time(), 
            note=note, 
            velocity=velocity)
        elif value['type'] == 'note_off':
            note = value['note']
            if note in self.presses:
                del self.presses[note]
