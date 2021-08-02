#!/usr/bin/env python


import datetime
from rgb.utilities import sustain_off, sustain_on
import logging
import os
import time
from dataclasses import dataclass
from random import randrange
from typing import Dict, Optional, Set, Tuple
from rgb.constants import NUM_NOTES, MIDI_DIAL_MAX

from rgb.form.baseform import BaseForm


log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))

@dataclass(frozen=True)
class Press():
    t: float
    note: int
    velocity: int

    @property
    def note_index(self):
        return self.note % NUM_NOTES

class KeyAwareForm(BaseForm):
    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
        self.presses: Dict[str, Press] = dict()
        
        # None means sustain is off.
        self.released_presses_sustained: Optional[Set] = None

    def cleanup(self):
        self.presses = dict()
    
    def midi_handler(self, value: Dict):
        # Key Press: msg.dict() -> {'type': 'note_on', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0} {'type': 'note_off', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0}
        if value['type'] == 'note_on':
            note = value['note']
            velocity = value['velocity'] / MIDI_DIAL_MAX
            self.presses[note] = Press(t=time.time(), note=note, velocity=velocity)
        elif value['type'] == 'note_off':
            note = value['note']
            # If it is sustained, it will be deleted by the sustain off event.
            if self.released_presses_sustained is not None:
                self.released_presses_sustained.add(note)
            elif note in self.presses:
                del self.presses[note]
        elif sustain_on(value):
            #TODO DEBUG 
            log.info("Sustain on.")
            if self.released_presses_sustained is not None:
                log.warning("Handling a sustain while released_presses_sustained is already defined. Replacing set of sustained keys.")    
            self.released_presses_sustained = set(self.presses.keys())
        elif sustain_off(value):
        #TODO DEBUG 
            log.info("Sustain off.")
            if self.released_presses_sustained is None:
                log.warning("Handling a sustain-off while released_presses_sustained is None, ignoring.")
                return
            self.presses = {k:v for k,v in self.presses.items() if k not in self.released_presses_sustained}
            self.released_presses_sustained = None

            