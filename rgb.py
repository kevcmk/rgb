#!/usr/bin/env python

import random
import json
from typing import List, Set, Tuple
from samplebase import SampleBase
import math
from random import randrange
import time
from dataclasses import dataclass
import colorsys

@dataclass
class Elt:
    def __init__(self):
        self.x: float = random.random()
        self.y: float = random.random()
        self.hue: float = random.random()
        self.born: float = time.time()
        self.lifespan: float = 10 * random.random()
    
    def __str__(self):
        return json.dumps({key: getattr(self, key) for key in ["x","y","hue","born","lifespan","age", "alive", "luminance"]})

    def __hash__(self):
        return hash((self.x, self.y, self.hue))
    
    def __eq__(self, other):
        return hash(self) == hash(other)

    @property
    def age(self) -> float:
        return time.time() - self.born
    
    @property
    def alive(self) -> bool:
        return self.age <= self.lifespan

    @property
    def luminance(self):
        return self.age / self.lifespan
        #sqr = self.age ** 2
        #t = self.age / self.lifespan
        #res = sqr / (2.0 * (sqr - t) + 1.0)
        #return min(1.0, res * 2)
        
    
class Rgb(SampleBase):
    def __init__(self, *args, **kwargs):
        super(Rgb, self).__init__(*args, **kwargs)
        

    def run(self):
        hz = 60
        population = 512
        offset_canvas = self.matrix.CreateFrameCanvas()
        elts: Set[Elt] = {Elt() for _ in range(population)}
        
        while True:
            
            elts = set(filter(lambda x: x.alive, elts))
            elts.update([Elt() for _ in range(population - len(elts))])
                    
            offset_canvas.Clear()

            for elt in elts:
                
                if elt.alive:
                    rgb = colorsys.hsv_to_rgb(elt.hue, 1.0, elt.luminance)
                    # print(elt)
                    offset_canvas.SetPixel(
                        int(self.matrix.width * elt.x), 
                        int(self.matrix.height * elt.y), 
                        int(rgb[0] * 255), 
                        int(rgb[1] * 255), 
                        int(rgb[2] * 255)
                    )
                
            time.sleep(1 / hz)
            offset_canvas = self.matrix.SwapOnVSync(offset_canvas)
            


# Main function
if __name__ == "__main__":
    rgb = Rgb()
    if (not rgb.process()):
        rgb.print_help()
