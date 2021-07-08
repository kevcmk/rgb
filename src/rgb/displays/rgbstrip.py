
import time
from rpi_ws281x import PixelStrip, Color
import argparse
import atexit 
import os

class RGBStrip:

    def __init__(self, height: int):

        LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
        # LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
        LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
        LED_DMA = 10          # DMA channel to use for generating signal (try 10)
        LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
        LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
        LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
        
        self.hz = 40

        self.strip: PixelStrip = PixelStrip(height, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        # Intialize the library (must be called once before other functions).
        self.strip.begin()
        atexit.register(lambda: self.clear())

        self.height = self.strip.numPixels()
        
        print(f"Running chase @ {self.height}...")    
        
    def blocking_loop(self):
        i = 0
        while True:
            i += 1
            self.strip.setPixelColor((i - 0) % self.height, Color(255, 0, 0))
            self.strip.setPixelColor((i - 1) % self.height, Color(127, 0, 0))
            self.strip.setPixelColor((i - 2) % self.height, Color(63, 0, 0))
            self.strip.setPixelColor((i - 3) % self.height, Color(31, 0, 0))
            self.strip.setPixelColor((i - 4) % self.height, Color(15, 0, 0))
            self.strip.setPixelColor((i - 4) % self.height, Color(7, 0, 0))
            self.strip.setPixelColor((i - 5) % self.height, Color(3, 0, 0))
            self.strip.setPixelColor((i - 6) % self.height, Color(1, 0, 0))
            self.strip.setPixelColor((i - 7) % self.height, Color(0, 0, 0))
            self.strip.show()
            time.sleep(1 / self.hz)
            


    def clear(self):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(0,0,0))
        self.strip.show()

