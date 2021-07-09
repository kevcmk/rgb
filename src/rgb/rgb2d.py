
import colorsys
import datetime
import json
import logging
import multiprocessing
import os
import sys
import time
from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
from json.decoder import JSONDecodeError
from typing import Dict, NamedTuple

import numpy as np
import numpy.typing as npt
from PIL import Image
from rgbmatrix import RGBMatrix, FrameCanvas

import constants
import imaqt
from hzel_samplebase import SampleBaseMatrixFactory
from messages import Button, Dial, Switch

from forms import gravity
from forms import keys
from forms import orbit
from forms import shape
from forms import stars
from forms import stripes
from forms import timer


log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))


class RGB2D():

    def parse_hzeller_rgb_args(self):
        rgb_args = {k:v for k,v in os.environ.items() if k.startswith("RUN_ARG_")}
        for k,v in rgb_args.items():
            log.debug(f"Parsing rgb_arg: {k}: {v}")
            argparse_style_arg = "--" + k.replace("RUN_ARG_", "").replace("_", "-").lower()
            log.info(f"Arg-parsing: {argparse_style_arg}: {v}")
            sys.argv.extend([argparse_style_arg, v])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.max_hz = 60
        
        self.matrix_width = int(os.environ["MATRIX_WIDTH"])
        self.matrix_height = int(os.environ["MATRIX_HEIGHT"])

        self.parse_hzeller_rgb_args()
        self.matrix: RGBMatrix = SampleBaseMatrixFactory().from_argparse()
        # Documentation: https://github.com/hzeller/rpi-rgb-led-matrix/blob/dfc27c15c224a92496034a39512a274744879e86/include/led-matrix.h#L204
        # for explanation
        # Explanation: https://github.com/hzeller/rpi-rgb-led-matrix/blob/dfc27c15c224a92496034a39512a274744879e86/bindings/python/samples/rotating-block-generator.py#L42
        self.offset_canvas: FrameCanvas = self.matrix.CreateFrameCanvas()
        def _set_framecanvas(image: Image.Image) -> FrameCanvas:
            self.offset_canvas.SetImage(image)
            self.offset_canvas = self.matrix.SwapOnVSync(self.offset_canvas)
        self.set_framecanvas = _set_framecanvas
                    
        #                         ⬅
        (self.clicker_receiver_cxn, self.clicker_sender_cxn) = multiprocessing.Pipe(duplex=False)
        #                         ⬅
        (self.midi_receiver_cxn, self.midi_sender_cxn) = multiprocessing.Pipe(duplex=False)

        def button_callback(client, userdata, msg):
            decoded = msg.payload.decode('utf-8')
            log.debug(f"Button callback invoked with message: {decoded}")
            
            try:
                o = json.loads(decoded)
            except JSONDecodeError as e:
                log.info("Failed to parse JSON; aborting. Message: {decoded}", e)
                return

            if o["message"] == "button":
                log.info(f"Got button press: {o}")
                self.clicker_sender_cxn.send(Button(index=o["index"], state=o["state"]))
            elif o["message"] == "switch":
                log.info(f"Got switch change: {o}")
                self.clicker_sender_cxn.send(Switch(index=o["index"], state=o["state"]))
            elif o["message"] == "dial":
                log.info(f"Got dial change: {o}")
                self.clicker_sender_cxn.send(Dial(index=o["index"], state=o["state"]))
            else:
                log.warning(f"Unrecognized message {o}")
                
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
        button_topic = os.environ["CONTROL_TOPIC"]
        ima.client.message_callback_add(button_topic, button_callback)
        midi_topic = os.environ["MIDI_CONTROL_TOPIC"]
        ima.client.message_callback_add(midi_topic, midi_callback)
        ima.connect()
        ima.client.subscribe(button_topic)
        ima.client.subscribe(midi_topic)

        dimensions = (self.matrix_width, self.matrix_height)
        self.forms = (
            # timer.Timer(dimensions),
            # stripes.Stripes(dimensions),
            stars.Stars(dimensions), 
            keys.Keys(dimensions), 
            orbit.Orbit(dimensions, fast_forward_scale=60 * 60 * 24 * 30), 
            gravity.Gravity(dimensions, 0.006, 32), 
            shape.Shape(dimensions), 
        )
        self.form_index = 0
                
        self.handlers = {
            "Button": {
                2: lambda state: self.next_form(state)
            }
        }

    @property
    def max_dt(self):
        # +1 to prevent 
        return 1 / (self.max_hz + 1)

    @property
    def form(self):
        return self.forms[self.form_index]
    
    # Button handler, when true change state
    def next_form(self, state):
        if state:
            self.form.cleanup()
            self.form_index = (self.form_index + 1) % len(self.forms)
        
    def previous_form(self, state):
        if state:
            self.form.cleanup()
            self.form_index = (self.form_index - 1) % len(self.forms)
    
    def midi_handler(self, value: Dict):
        # Key Press: msg.dict() -> {'type': 'note_on', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0} {'type': 'note_off', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0}
        # Note, this overlaps with the piano keys on a mid-octave
        if value['type'] == 'note_on' and value['note'] == constants.PAD_INDICES[0]:
            # pad 0
            self.previous_form(True)
        elif value['type'] == 'note_on' and value['note'] == constants.PAD_INDICES[1]:
            # pad 1
            self.next_form(True)
        # elif value['type'] == 'control_change' and value['control'] == 17: # MIDI #3
        #     self.max_hz = value['value'] * 3 # [0,381]
        #     log.info(f"Set max_hz to {self.max_hz}")

    def blocking_loop(self):

        log.info(f"Running {self.form} at maximum {self.max_hz} Hz...")
        
        t_start = time.time()
        t_last = t_start
        
        while True:

            now = time.time()
            total_elapsed_since_last_frame = now - t_last
            t_last, wait_time = now, self.max_dt - total_elapsed_since_last_frame
            if wait_time < 0:
                log.debug(f"Frame dt exceeded: {wait_time}")
            else:
                time.sleep(wait_time)    
            
            image = self.form.step(total_elapsed_since_last_frame)
            self.set_framecanvas(image)
            
            while self.midi_receiver_cxn.poll(0):
                value = self.midi_receiver_cxn.recv()
                log.info(f"midi_receiver_cxn received: {value}")
                # If form midi handler goes first, then a pad strike that is also a valid key press does not induce that form's key's effect.
                self.form.midi_handler(value)
                self.midi_handler(value)
            
            while self.clicker_receiver_cxn.poll(0):
                value = self.clicker_receiver_cxn.recv()
                log.info(f"clicker_receiver_cxn received: {value}")
                
                message_type = type(value).__name__
                index = value.index
                state = value.state
                
                log.info(f"{message_type} -> {index}, {state}")        
                for target in (self, self.form):
                    try:            
                        target.handlers[message_type][index](state)
                    except KeyError as e:
                        log.debug(f"No handler for {value} on {target}")
                        continue
                    else: 
                        # If a handler succeeds, break.
                        log.debug(f"Handler succeeded for {target}")
                        break

        
if __name__ == "__main__":
    rgb2d = RGB2D()
    rgb2d.blocking_loop()

