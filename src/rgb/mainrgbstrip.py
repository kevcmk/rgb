import os
from rgb.display.ledstrip import LedStrip
from rgb.controlloop import ControlLoop
from rgb.form import (audio_spectrogram, gravity, orbit, sustainobject, stars, timer, basenoise)

import logging
log = logging.getLogger(__name__)

if __name__ == "__main__":

    dimensions = (int(os.environ.get("LED_COUNT", 100)), 1)
    led_pind = int(os.environ.get("LED_PIN", 18))
    led_brightness = int(os.environ.get("RGB_STRIP_LED_BRIGHTNESS", 255))

    log.info("Initializing LedStrip with led_pin {led_pin}, led brightness {led_brightness}, and dimensions {led_count}")
    display = LedStrip(dimensions=dimensions, led_pin=led_pind, led_brightness=led_brightness, skip_first_n=0)
    
    forms = (
        # stripes.Stripes(dimensions),
        sustainobject.VerticalNotes(dimensions), 
        # sustainobject.VerticalKeys(dimensions),
        # orbit.Orbit(dimensions, fast_forward_scale=60 * 60 * 24 * 30), 
    )
    rgb1d = ControlLoop(display=display, forms=forms)
    rgb1d.initialize_mqtt()
    rgb1d.blocking_loop()
