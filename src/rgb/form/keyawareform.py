#!/usr/bin/env python


from rgb.utilities import sustain_off, sustain_on
import logging
import os
import time
from dataclasses import dataclass
from random import randrange
from typing import Dict, Tuple
from constants import NUM_NOTES, MIDI_DIAL_MAX

from rgb.form.baseform import BaseForm


log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))

@dataclass(frozen=True)
class Press():
    t: float
    note: int
    velocity: int

    @property
    def index(self):
        return self.note % NUM_NOTES

class KeyAwareForm(BaseForm):
    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
        self.presses: Dict[str, Press] = dict()

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

class SustainAwareForm(KeyAwareForm):
    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
        print("Sustainaware")
        self.sustain = False

    def cleanup(self):
        self.presses = dict()
    
    def midi_handler(self, value: Dict):
        # Key Press: msg.dict() -> {'type': 'note_on', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0} {'type': 'note_off', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0}
        super().midi_handler(value)
        if sustain_on(value):
            self.sustain = True
        elif sustain_off(value):
            self.sustain = False
            