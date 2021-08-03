#!/usr/bin/env python


from rgb.utilities import dial
import logging
import os
import time
from dataclasses import dataclass
from typing import Dict, Tuple, Union

import numpy as np
from noise import pnoise3, snoise3
from PIL import Image
from rgb.form.keyawareform import KeyAwareForm
from rgb.constants import NUM_NOTES, MIDI_DIAL_MAX
from rgb.form.baseform import BaseForm
from rgb.utilities import hsv_to_pixel, dial

log = logging.getLogger(__name__)
log.setLevel(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))


class BaseNoise(BaseForm):

    NOISE_FUNCTIONS = [pnoise3, snoise3]
    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
        self.presses = dict()

        self.noise_function_index = 0
        self.scale = 1 / 36.0 # 1/48, [0.1, 10]
        self.octaves = 4 # 4, [1, 8]
        self.persistence = 0.0001 # 0.25, [0, 5]
        self.timescale = 0.25
        
        self.t_start = time.time()
    
    def midi_handler(self, value: Dict):
        if dial(0, value):
            self.scale = (value['value'] / MIDI_DIAL_MAX) ** 3 # [0, 1.0] 🏒🏒 
            log.info(f"Scale set to {self.scale}")
        elif dial(1, value):
            self.octaves = int(value['value'] / MIDI_DIAL_MAX * 8) + 1  # [1, 9]
            log.info(f"Octaves set to {self.octaves}")
        elif dial(2, value):
            self.persistence = (value['value'] / MIDI_DIAL_MAX) ** 2 # [0, 1.0] 🏒 
            log.info(f"Persistence set to {self.persistence}")
        elif dial(3, value):
            self.timescale = value['value'] / MIDI_DIAL_MAX # [0, 1.0] linear
            log.info(f"Timescale set to {self.timescale}")
        
    def select_noise(self, x, y, z) -> float:
        return self.NOISE_FUNCTIONS[self.noise_function_index](y * self.scale, x * self.scale, z * self.timescale, octaves=self.octaves, persistence=self.persistence)

    @staticmethod
    def normalize_noise(noise: float) -> float:
        return (noise + 1.0) / 2

    def noise_to_pixel(self, v: float):
        normed = BaseNoise.normalize_noise(v)
        pix_value = normed * 255
        return (np.uint8(pix_value),np.uint8(pix_value),np.uint8(pix_value))
    
    def step(self, dt) -> Image.Image:
        res = np.zeros((self.matrix_height, self.matrix_width, 3), dtype=np.uint8)
        dt = time.time() - self.t_start
        half_width = self.matrix_width // 2
        half_height = self.matrix_height // 2
        for i in range(self.matrix_height):
            for j in range(self.matrix_width):
                v = self.select_noise(x=j - half_width, y=i - half_height, z=dt)
                res[i,j,:] = self.noise_to_pixel(v)
        
        return Image.fromarray(res) #.transpose(Image.FLIP_TOP_BOTTOM)



class WhispNoise(BaseNoise): 
    def noise_to_pixel(self, v: float):
        normed = (v + 1.0) / 2
        exponented = normed ** 8
        pix_value = max(1.0, exponented * 255.0)
        return (np.uint8(pix_value),np.uint8(pix_value),np.uint8(pix_value))
        

class HueNoise(BaseNoise):
    def __init__(self, dimensions: Tuple[int, int]):
        super().__init__(dimensions)
        self.scale = 1 / 36.0 # 1/48, [0.1, 10]
        self.octaves = 4 # 4, [1, 8]
        self.persistence = 0.0001 # 0.25, [0, 5]
        self.timescale = 0.25
        
    def noise_to_pixel(self, v: float):
        return hsv_to_pixel((v + 1.0) / 2, 1.0, 1.0)


class NoiseKey(BaseNoise, KeyAwareForm):
        
    def step(self, dt) -> Union[Image.Image, np.ndarray]:
        time_elapsed = time.time() - self.t_start
        notespace = np.zeros((len(self.presses), self.matrix_height, self.matrix_width, 3), dtype=np.uint8)
        xs = np.linspace(start=0, stop=self.matrix_width, num=NUM_NOTES + 1, endpoint=True, dtype=np.uint8)
        for index, v in enumerate(self.presses.values()):
            note_index = v.note % NUM_NOTES
            hue = note_index / NUM_NOTES
            lo = xs[note_index]
            hi = xs[note_index + 1] 
            for i in range(self.matrix_height):
                for j in range(self.matrix_width):
                    noise_value = self.NOISE_FUNCTIONS[self.noise_function_index](
                        i * self.scale, j * self.scale, 
                        time_elapsed * self.timescale, 
                        octaves=self.octaves, 
                        persistence=note_index / 12)
                    pixel = self.noise_to_pixel(noise_value) 
                    notespace[index, i, j, 0] = pixel[0]
                    notespace[index, i, j, 1] = pixel[1]
                    notespace[index, i, j, 2] = pixel[2] 

        res = np.mean(notespace, axis=0, dtype=np.uint8)


        return res