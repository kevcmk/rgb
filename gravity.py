#!/usr/bin/env python

import random
import json
from typing import List, Set, Tuple
import math
from random import randrange
import time
from dataclasses import dataclass
import colorsys
import logging
import os

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

log = logging.getLogger(__name__)
logging.basicConfig(level=os.environ.get("PYTHON_LOG_LEVEL", "INFO"))

@dataclass
class Elt:
    def __init__(self, y, x):
        self.y: float = y
        self.x: float = x
        self.vy: float = 0
        self.hue: float = random.random()
        
    def __str__(self):
        return json.dumps({key: getattr(self, key) for key in ["x","y","vy"]})

    def __hash__(self):
        return hash((self.x, self.y, self.hue))
    
    def __eq__(self, other):
        return hash(self) == hash(other)
    
class Gravity():
    def __init__(self, height, width, *args, **kwargs):
        super(Gravity, self).__init__(*args, **kwargs)
        
        self.height = height
        self.width = width
        
        
    def run(self):

        # https://matplotlib.org/stable/gallery/animation/dynamic_image.html

        fig, ax = plt.subplots()

        hz = 60
        dt = 1 / hz
        population = 10
        
        # ims is a list of lists, each row is a list of artists to draw in the
        # current frame; here we are just animating one artist, the image, in
        # each frame
        
        ims = []
        elts = set()

        for i in range(30):
            
            elts = set(filter(lambda e: e.y >= 0, elts))
            elts.update([Elt(y=float(random.randint(0, self.height - 1)), x=float(random.randint(0, self.width - 1))) for _ in range(population - len(elts))])
            log.info(elts)
            for elt in elts:
                img = np.zeros((self.height, self.width, 3))
                
                
                rgb = colorsys.hsv_to_rgb(elt.hue, 1.0, 1.0)
                elt.vy = elt.vy + (-9.8 * dt)
                elt.y = elt.y + (elt.vy * dt)
                log.info(elt)
                img[round(elt.y),round(elt.x),:] = rgb
                log.info(img)
                
                im = ax.imshow(img, animated=True)
                if i == 0:
                    ax.imshow(img)  # show an initial one first
                ims.append([im])

            
        ani = animation.ArtistAnimation(fig, ims, interval=200, blit=True,
                                        repeat_delay=1000)

        # To save the animation, use e.g.
        #
        # ani.save("movie.mp4")
        #
        # or
        #
        # writer = animation.FFMpegWriter(
        #     fps=15, metadata=dict(artist='Me'), bitrate=1800)
        # ani.save("movie.mp4", writer=writer)

        plt.show()


       


# Main function
if __name__ == "__main__":
    gravity = Gravity(height=32, width=32)
    gravity.run()

