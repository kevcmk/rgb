
import json
import logging
import multiprocessing
import os
import time
from dataclasses import dataclass
from json.decoder import JSONDecodeError
from typing import Dict

import numpy as np
import numpy.typing as npt
from PIL import Image
from rpi_ws281x import Color

import constants
import imaqt
from displays.rgbstrip import RGBStrip
from forms.chase import Chase

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))


class RGB1D():

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_hz = 60
        self.height = int(os.environ["LED_COUNT"])
        self.rgb_strip = RGBStrip(height=self.height)
        #                       ⬅
        (self.midi_receiver_cxn, self.midi_sender_cxn) = multiprocessing.Pipe(duplex=False)

        self.bootstrap_midi_listener()
        self.form = Chase(self.height)

    def bootstrap_midi_listener(self):
        def midi_callback(client, userdata, msg):
            decoded = msg.payload.decode('utf-8')
            log.debug(f"Midi callback invoked with message: {decoded}")
            try:
                o = json.loads(decoded)
            except JSONDecodeError as e:
                log.info("Failed to parse JSON; aborting. Message: {decoded}", e)
                return
            self.midi_sender_cxn.send(o)

            log.debug(f"Got midi control message: {o}")
        
        ima = imaqt.IMAQT.factory()
        midi_topic = os.environ["MIDI_CONTROL_TOPIC"]
        ima.client.message_callback_add(midi_topic, midi_callback)
        ima.connect()
        ima.client.subscribe(midi_topic)

    @property
    def max_dt(self):
        # +1 to prevent 
        return 1 / (self.max_hz + 1)
        
    def midi_handler(self, value: Dict):
        # Key Press: msg.dict() -> {'type': 'note_on', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0} {'type': 'note_off', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0}
        # Note, this overlaps with the piano keys on a mid-octave
        if value['type'] == 'note_on' and value['note'] == constants.PAD_INDICES[0]:
            # pad 0
            pass
        elif value['type'] == 'note_on' and value['note'] == constants.PAD_INDICES[1]:
            # pad 1
            pass
        # elif value['type'] == 'control_change' and value['control'] == 17: # MIDI #3
        #     self.max_hz = value['value'] * 3 # [0,381]
        #     log.info(f"Set max_hz to {self.max_hz}")


    def render(self, total_elapsed_since_last_frame: float):
        image = self.form.step(total_elapsed_since_last_frame)
        for i in range(self.height):
            self.strip.setPixelColor(i, Color(image[i,0],image[i,1],image[i,2]))
        self.set_framecanvas(image)

    def interframe_sleep(self):
        now = time.time()
        total_elapsed_since_last_frame = now - self.t_last
        self.t_last, wait_time = now, self.max_dt - total_elapsed_since_last_frame
        if wait_time < 0:
            log.debug(f"Frame dt exceeded: {wait_time}")
        else:
            time.sleep(wait_time)
        return total_elapsed_since_last_frame
            
    def poll_midi(self):
        while self.midi_receiver_cxn.poll(0):
            value = self.midi_receiver_cxn.recv()
            log.info(f"midi_receiver_cxn received: {value}")
            # If form midi handler goes first, then a pad strike that is also a valid key press does not induce that form's key's effect.
            self.form.midi_handler(value)
            self.midi_handler(value)

    def blocking_loop(self):
        self.t_start = time.time()
        self.t_last = self.t_start
        while True:
            total_elapsed_since_last_frame = self.interframe_sleep()    
            self.render(total_elapsed_since_last_frame)
            self.poll_midi()

if __name__ == '__main__':
    rgb1d = RGB1D()
    rgb1d.blocking_loop()
