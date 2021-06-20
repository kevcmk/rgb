
import colorsys
from datetime import timedelta
import json
import logging
import multiprocessing
import os
import time
import datetime
import numpy as np
import numpy.typing as npt
from samplebase import SampleBase

import gravity
import imaqt
import timer

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
            
            o = json.loads(decoded)
            
            if o["message"] == "button" and o["index"] == "0" and o["state"] == "on":
                log.info("Got button 0 press")
                self.sender_cxn.send(-1)
            elif o["message"] == "button" and o["index"] == "1" and o["state"] == "on":
                log.info("Got button 1 press")
                self.sender_cxn.send(1)
            elif o["message"] == "switch" and o["index"] == "0" and o["state"] == "off":
                log.info("Got switch off")
                self.sender_cxn.send(False)
            elif o["message"] == "switch" and o["index"] == "0" and o["state"] == "on":
                log.info("Got switch on")
                self.sender_cxn.send(True)
        
        ima = imaqt.IMAQT.factory()
        button_topic = os.environ["CONTROL_TOPIC"]
        ima.client.message_callback_add(button_topic, button_callback)
        ima.connect()
        ima.client.subscribe(button_topic)

    def run(self):
        
        if self.args.form == "gravity":
            self.form = gravity.Gravity(64, 32, 0.320, 0.160, 60, 1)
        if self.args.form == "timer":
            self.form = timer.Timer(64, 32)
        else:
            raise ValueError(f"Unrecognized form: {self.parser.form}")

        hz = int(self.args.max_fps)
        dt = 1 / hz # Seconds
        log.info(f"Running gravity at {hz} Hz...")
        offset_canvas = self.matrix.CreateFrameCanvas()

        t_start = time.time()
        t_last = t_start
        
        while True:

            while self.receiver_cxn.poll(0):
                value = self.receiver_cxn.recv()
                if isinstance(self.form, gravity.Gravity):
                    self.form.population = max(1, self.form.population + value) # Prevent less than zero population
                    
                elif isinstance(self.form, timer.Timer):
                    if value == 1:
                        self.form.t_stop = (self.form.t_stop or datetime.datetime.utcnow()) + datetime.timedelta(minutes=1)
                    elif value == -1:
                        self.form.t_stop = None
                    elif value == True:
                        self.form.show = True
                    elif value == False:
                        self.form.show = False
                    
            a = time.time()
            matrix = self.form.step(dt)
            b = time.time()
            # for i,j,_ in np.ndindex(matrix.shape):
            #     offset_canvas.SetPixel(j, i, int(matrix[i,j][0] * 255), int(matrix[i,j][1] * 255), int(matrix[i,j][2] * 255))
            offset_canvas.SetImage(matrix)
            c = time.time()
            log.debug(f"{b - a} step, {c - b} step")
            offset_canvas = self.matrix.SwapOnVSync(offset_canvas)
            
            now = time.time()
            t_last, wait_time = now, dt - (now - t_last)
            if wait_time < 0:
                log.warning(f"Frame dt exceeded: {wait_time}")
            else:
                log.debug(f"Sleeping for {wait_time}")
                time.sleep(wait_time)

        
if __name__ == "__main__":
    b = BaseMatrix()
    if not b.process():
        b.print_help()

