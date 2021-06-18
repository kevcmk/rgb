import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import logging
import time
import json
from rgb.imaqt import IMAQT
import multiprocessing

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))

#            ⬅
(receiver_cxn, sender_cxn) = multiprocessing.Pipe(duplex=False)

def button_callback(client, userdata, msg):
    decoded = msg.payload.decode('utf-8')
    log.debug(f"Button callback invoked with message: {decoded}")
    
    o = json.loads(decoded)
    
    if o["index"] == "0" and o["state"] == "on":
        log.info("")
        sender_cxn.send(-1)
    elif o["index"] == "1" and o["state"] == "on":
        log.info("Got button 1 press")
        sender_cxn.send(1)
    else:
        log.warning(f"Couldn't process {o}")    




acc = 0
while True:
    time.sleep(2)
    while receiver_cxn.poll(0):
        value = receiver_cxn.recv()
        log.debug(f"Received value {value}")
        acc += value
    log.info(f"Acc: {acc}")
