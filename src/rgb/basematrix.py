
import colorsys
from dataclasses import dataclass
from datetime import timedelta
import json
from json.decoder import JSONDecodeError
import logging
import multiprocessing
import os
import time
import datetime
from typing import NamedTuple
import numpy as np
import numpy.typing as npt
from decimal import Decimal
from samplebase import SampleBase
from messages import Button, Dial, Switch

import gravity
import imaqt
import timer
import orbit


log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))


class BaseMatrix(SampleBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser.add_argument("-f", "--form", action="store", help="Extra Kevin argument. The form of LED to take.")
        self.parser.add_argument("--max-fps", action="store", help="Maximum frame rate")
        
        #            ⬅
        (self.receiver_cxn, self.sender_cxn) = multiprocessing.Pipe(duplex=False)

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
                self.sender_cxn.send(Button(index=o["index"], state=o["state"]))
            elif o["message"] == "switch":
                log.info(f"Got switch change: {o}")
                self.sender_cxn.send(Switch(index=o["index"], state=o["state"]))
            elif o["message"] == "dial":
                log.info(f"Got dial change: {o}")
                self.sender_cxn.send(Dial(index=o["index"], state=o["state"]))
            else:
                log.warning(f"Unrecognized message {o}")
                
        
        ima = imaqt.IMAQT.factory()
        button_topic = os.environ["CONTROL_TOPIC"]
        ima.client.message_callback_add(button_topic, button_callback)
        ima.connect()
        ima.client.subscribe(button_topic)

        self.orbit = orbit.Orbit(matrix_width=32, matrix_height=64, fast_forward_scale=60 * 60 * 24 * 30)
        self.gravity = gravity.Gravity(64, 32, 0.320, 0.160, 1)
        self.timer = timer.Timer(64, 32)
        self.forms = [self.orbit, self.gravity, self.timer]
        self.form_index = 0
                
        self.handlers = {
            "Button": {
                0: lambda state: self.previous_form(state),
                1: lambda state: self.next_form(state)
            }
        }
     
    
    @property
    def form(self):
        return self.forms[self.form_index]
    
    # Button handler, when true change state
    def next_form(self, state):
        if state:
            self.form_index = (self.form_index + 1) % len(self.forms)
        
    def previous_form(self, state):
        if state:
            self.form_index = (self.form_index - 1) % len(self.forms)
    
    def run(self):

        hz = int(self.args.max_fps)
        dt = 1 / hz # Seconds
        log.info(f"Running {self.args.form} at {hz} Hz...")
        offset_canvas = self.matrix.CreateFrameCanvas()

        t_start = time.time()
        t_last = t_start
        
        while True:

            while self.receiver_cxn.poll(0):
                value = self.receiver_cxn.recv()
                log.info(f"Received value {value}")

                for target in (self, self.form):
                    try:    
                        log.info(f"{value.__name__} -> {value.index}, {isinstance(value, Button) or isinstance(value, Switch) or isinstance(value, Dial)}")        
                        if isinstance(value, Button) or isinstance(value, Switch) or isinstance(value, Dial):
                            self.form.handlers[value.__name__][value.index].apply(value.statue)
                            
                    except AttributeError as e:
                        log.debug(f"No handler for {value} on {target}")
                        continue
                    else: 
                        # If a handler succeeds, break.
                        log.debug(f"Handler succeeded for {target}")
                        break

                # if value == "on":
                #     self.form = self.timer
                # elif value == "off":
                #     self.form = self.gravity
                # elif isinstance(self.form, gravity.Gravity):
                #     self.form.population = max(1, self.form.population + value) # Prevent less than zero population
                # elif isinstance(self.form, timer.Timer):
                #     if value == 1:
                #         self.form.t_stop = (self.form.t_stop or datetime.datetime.utcnow()) + datetime.timedelta(minutes=1)
                #     elif value == -1:
                #         self.form.t_stop = None
                    
                    
            a = time.time()
            matrix = self.form.step(dt)
            b = time.time()
            # for i,j,_ in np.ndindex(matrix.shape):
            #     offset_canvas.SetPixel(j, i, int(matrix[i,j][0] * 255), int(matrix[i,j][1] * 255), int(matrix[i,j][2] * 255))
            offset_canvas.SetImage(matrix)
            c = time.time()
            offset_canvas = self.matrix.SwapOnVSync(offset_canvas)
            
            now = time.time()
            t_last, wait_time = now, dt - (now - t_last)
            if wait_time < 0:
                log.warning(f"Frame dt exceeded: {wait_time}")
            else:
                time.sleep(wait_time)

        
if __name__ == "__main__":
    b = BaseMatrix()
    if not b.process():
        b.print_help()

