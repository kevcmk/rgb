
from rgb.display.basedisplay import BaseDisplay
from numpy.core.fromnumeric import shape
import logging
from typing import Tuple, Union
from rpi_ws281x import PixelStrip, Color

import numpy as np
from PIL import Image

import atexit 
import os

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))

class LedStrip(BaseDisplay):

    def __init__(self, dimensions: Tuple[int, int], led_pin: int=18, led_brightness: int=255, skip_first_n: int=0):
        super().__init__(dimensions)
        if dimensions[1] != 1:
            raise ValueError("Height (2nd dimension) of RGB Strip must be 1.")

        # TODO Use dimensions in conjunction with skip_first_n?
        self.dimensions = dimensions
        # If present, don't illuminate the first n values
        self.skip_first_n: int = skip_first_n

        # GPIO pin connected to the pixels (18 uses PWM!).
        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
        LED_PIN = led_pin     

        LED_BRIGHTNESS = led_brightness  # Set to 0 for darkest and 255 for brightest
        
        
        LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
        LED_DMA = 10          # DMA channel to use for generating signal (try 10)
        LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
        LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
        
        self.rgb_strip: PixelStrip = PixelStrip(self.dimensions[0], LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        # Intialize the library (must be called once before other functions).
        self.rgb_strip.begin()
        atexit.register(lambda: self.clear())

        self.height = self.rgb_strip.numPixels()
        
    def clear(self):
        # If you ever want to direct-display:
        # import numpy as np; from rgb.display.ledstrip import LedStrip;
        # a = LedStrip((100,1), 10, 0)
        # a.display(np.tile(np.array((255,255,255)), (100, 1)))
        for i in range(self.rgb_strip.numPixels()):
            self.rgb_strip.setPixelColor(i, Color(0,0,0))
        self.rgb_strip.show()

    
    def display(self, image: Union[Image.Image, np.ndarray]):
        if isinstance(image, np.ndarray):
            arr = image
        elif isinstance(image, Image.Image):
            arr = np.array([image.getpixel((i,0)) for i in range(image.width)])
        else:
            raise ValueError(f"Invalid type @ display: {type(image)}")
        for i in range(self.skip_first_n, self.height):
            rgb = arr[i]
            self.rgb_strip.setPixelColor(
                i, 
                Color(
                    int(rgb[0]),
                    int(rgb[1]),
                    int(rgb[2])
                )
            )
        self.rgb_strip.show()