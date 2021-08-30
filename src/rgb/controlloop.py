
import datetime
from rgb.parameter_tuner import ParameterTuner
from rgb.form.baseform import BaseForm

import json
import logging
import multiprocessing
from multiprocessing import connection
import os
import time
from json.decoder import JSONDecodeError
from typing import Dict, Iterable, Optional

from rgb.imaqt import IMAQT
from rgb.display.basedisplay import BaseDisplay
from rgb.messages import Button, Dial, Spectrum, Switch
from rgb.utilities import loopwait

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))


class ControlLoop():

    def __init__(self, display: BaseDisplay, forms: Iterable[BaseForm]):
        self.max_hz = 60
        self.display = display

        self.clicker_receiver_cxn: Optional[connection.Connection] = None
        self.clicker_sender_cxn: Optional[connection.Connection] = None
        self.midi_receiver_cxn: Optional[connection.Connection] = None
        self.midi_sender_cxn: Optional[connection.Connection] = None
        self.brightness = 1.0
        
        self.forms = forms
        
        self.form_index = 0
                

    def initialize_mqtt(self):
        #                         ⬅
        (self.clicker_receiver_cxn, self.clicker_sender_cxn) = multiprocessing.Pipe(duplex=False)
        #                         ⬅
        (self.midi_receiver_cxn, self.midi_sender_cxn) = multiprocessing.Pipe(duplex=False)

        def button_callback(client, userdata, msg):
            decoded = msg.payload.decode('utf-8')
            log.debug(f"Button callback invoked with message: {decoded}")

            if not self.clicker_sender_cxn:
                log.warning("No sender connection in button_callback")
                return
            
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
            elif o["message"] == "spectrum":
                log.info(f"Got dial change: {o}")
                self.clicker_sender_cxn.send(Spectrum(index=o["index"], state=o["state"]))
            else:
                log.warning(f"Unrecognized message {o}")
                
        def midi_callback(client, userdata, msg):
            decoded = msg.payload.decode('utf-8')
            log.debug(f"Midi callback invoked with message: {decoded}")

            if not self.midi_sender_cxn:
                log.warning("No sender connection in midi_callback")
                return
            
            try:
                o = json.loads(decoded)
            except JSONDecodeError as e:
                log.info("Failed to parse JSON; aborting. Message: {decoded}", e)
                return
            self.midi_sender_cxn.send(o) 
            latency = f"(Latency {datetime.datetime.utcnow() - datetime.datetime.fromisoformat(o['midi_read_time'])})" \
                if 'midi_read_time' in o \
                else ''
            log.debug(f"Received MIDI control message: {o} {latency}")

       
        self.handlers = {
            "Button": {
                0: lambda state: self.previous_form(state),
                1: lambda state: self.next_form(state),
                2: lambda state: self.first_form()
            },
            "Dial": {
                0: lambda state: self.set_brightness(state),
            }
        }

        ima = IMAQT.factory()
        button_topic = os.environ["CONTROL_TOPIC"]
        ima.client.message_callback_add(button_topic, button_callback)
        midi_topic = os.environ["MIDI_CONTROL_TOPIC"]
        ima.client.message_callback_add(midi_topic, midi_callback)
        ima.connect()
        ima.client.subscribe(button_topic)
        ima.client.subscribe(midi_topic)

    @property
    def max_dt(self):
        # +1 to prevent 
        return 1 / (self.max_hz + 1)

    @property
    def form(self):
        return self.forms[self.form_index]
    
    def first_form(self):
        # So all sync to same form
        self.form.cleanup()
        self.form_index = 0
    
    # Button handler, when true change state
    def next_form(self, state):
        if state:
            self.form.cleanup()
            self.form_index = (self.form_index + 1) % len(self.forms)
    
    def previous_form(self, state):
        if state:
            self.form.cleanup()
            self.form_index = (self.form_index - 1) % len(self.forms)

    def set_brightness(self, state):
        self.brightness = state
        if state > 0.5: 
            # Ignore this if it's high
            log.info("Brightness tuned, but >0.5 so ignoring entirely.")
            pass
        if state < 0.5:
            brightness_value = int(ParameterTuner.linear_scale(state * 2, 0, 255))
            try:
                # TODO Abstract into display BaseDisplay
                self.display.matrix.set_brightness(brightness_value)
            except AttributeError as e:
                log.exception("Brightness tuned, but display brightness setting not supported.", e)
            
    
    def midi_handler(self, value: Dict):
        # Key Press: msg.dict() -> {'type': 'note_on', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0} {'type': 'note_off', 'time': 0, 'note': 48, 'velocity': 127, 'channel': 0}
        # Note, this overlaps with the piano keys on a mid-octave
        # if pad(0, value):
        #     # pad 0
        #     self.previous_form(True)
        # elif pad(1, value):
        #     # pad 1
        #     self.next_form(True)
        # elif button_mod(value):
        #     self.first_form()
        # elif button_sus(value):
        #     log.warning("Invoking exit on Suspend push")
        #     sys.exit(1)
        # elif value['type'] == 'control_change' and value['control'] == 17: # MIDI #3
        #     self.max_hz = value['value'] * 3 # [0,381]
        #     log.info(f"Set max_hz to {self.max_hz}")
        pass

    def blocking_loop(self):

        log.info(f"Running {self.form} at maximum {self.max_hz} Hz...")
        
        t_start = time.time()
        t_last = t_start
        
        while True:

            # TODO After?
            t_last, total_elapsed_since_last_frame = loopwait(t_last, self.max_dt)    
            
            image = self.form._instrumented_step(total_elapsed_since_last_frame)
            self.display.display(image)
            
            if self.midi_receiver_cxn:
                while self.midi_receiver_cxn.poll(0):
                    value = self.midi_receiver_cxn.recv()
                    log.info(f"midi_receiver_cxn received: {value}")
                    # If form midi handler goes first, then a pad strike that is also a valid key press does not induce that form's key's effect.
                    self.form.midi_handler(value)
                    self.midi_handler(value)

            if self.clicker_receiver_cxn:    
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
