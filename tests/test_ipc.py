import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import logging
import time
from json import JSONDecodeError

from rgb.imaqt import IMAQT

log = logging.getLogger(__name__)

ima = IMAQT.factory()
hz = 1
button_topic = "endor" # os.environ["BUTTON_CONTROL_TOPIC"]



# (child_cxn, parent_cxn) = multiprocessing.Pipe(duplex=False)

def button_callback(client, userdata, msg):
    log.info(f"Callback invoked message: {msg}")
    decoded = msg.payload.decode('utf-8')
    # try:
    #     o = json.loads(decoded)
    # except JSONDecodeError as e:
    #     log.warning(f"JSONDecode error decoding {decoded}", e)
    #     raise
    # if "index" in o and "state" in o:
    #     if "index" == "0" and "state" == "on":
    #         log.info("Got button 0 press")
    #         cxn.send(-1)
    #     elif "index" == "1" and "state" == "on":
    #         log.info("Got button 1 press")
    #         cxn.send(1)
    # else:
    #     log.warning(f"Couldn't process {o}")    

ima.client.message_callback_add(button_topic, button_callback)
ima.connect()



while True:
    time.sleep(1/hz)
    log.info("Beep.")
