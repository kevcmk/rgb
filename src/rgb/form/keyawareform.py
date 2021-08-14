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

@dataclass(frozen=False, order=True)
class Press():
    note: int
    velocity: int
    t: float
    
    # t_released Does not impact a note's hash or equality!!
    _t_released: Optional[float] = None

    def __hash__(self) -> int:
        return hash((self.note, self.velocity, self.t))
    
    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Press):
            return False
        else:
            return (self.note, self.velocity, self.t) == (o.note, o.velocity, o.t)

    @property
    def note_index(self):
        return self.note % NUM_NOTES
    
class KeyAwareForm(BaseForm):

    @staticmethod
    def is_expired(v, expire_after_s: float) -> bool:
        return v._t_released is not None and time.time() - v._t_released > expire_after_s
    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
        self.presses: Dict[str, Press] = dict()
        
        # None means sustain is off.
        self.sustain: bool = False

    def step(self, time_delta: float):
        self.prune_presses_dictionary()
        super().step(time_delta)

    def prune_presses_dictionary(self, expire_after_s: float = 1):
        if self.sustain:
            return
        self.presses = {k:v for k,v in self.presses.items() if not KeyAwareForm.is_expired(v, expire_after_s)}
        
    def cleanup(self):
        self.presses = dict()

    def midi_handler(self, value: Dict):
        # Key Press: msg.dict() -> {'type': 'note_on', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0} {'type': 'note_off', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0}
        log.info(value)
        if value['type'] == 'note_on':
            note = value['note']
            velocity = value['velocity'] / MIDI_DIAL_MAX
            self.presses[note] = Press(note=note, velocity=velocity, t=time.time())
        elif value['type'] == 'note_off':
            note = value['note']
            # If it is sustained, it will be deleted by the sustain off event.
            if note in self.presses:
                self.presses[note]._t_released = time.time()
            else:
                log.warning(f"Note off event for note {note} without a corresponding note in self.presses.")
        elif sustain_on(value):
            log.debug("Sustain on.")
            if self.sustain:
                log.warning("Handling a sustain while sustain is already defined. Replacing set of sustained keys.")    
            self.sustain = True
        elif sustain_off(value):
            log.debug("Sustain off.")
            if not self.sustain:
                log.warning("Handling a sustain-off while sustain is None, ignoring.")
                return
            self.sustain = False
            
            

            