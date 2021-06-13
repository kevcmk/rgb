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
    def __init__(self, matrix_height, matrix_width, *args, **kwargs):
        super(Gravity, self).__init__(*args, **kwargs)
        self.hz = 60
        self.steps = 250
        self.matrix_height: int = matrix_height
        self.matrix_width: int = matrix_width
        self.world_height: float = 0.320 # Meters 32x5mm
        self.world_width: float = 0.320 # Meters 32x5mm
        self.population = 100
        self.particles: Set[Elt] = set()
    
    def populate_particles(self):
        for i in range(self.population - len(self.particles)):
            self.particles.add(
                Elt(
                    y=self.world_height + random.uniform(0, self.world_height), 
                    x=random.uniform(0, self.world_width)
                ) 
            )
    @property
    def matrix_scale(self) -> float:
        # E.g. 1:4 would be 0.25
        return self.matrix_height / float(self.world_height)

    @property
    def dt(self):
        return 1 / self.hz
        
    def step(self, dt):
        for elt in self.particles:
            elt.vy = elt.vy + (-9.8 * dt) # -9.8 m/s^2
            elt.y = elt.y + (elt.vy * dt)
        self.particles = set(filter(lambda x: x.y >= 0, self.particles))

    def render(self):
        img = np.zeros((self.matrix_height, self.matrix_width, 3))
        for elt in self.particles:
            rgb = colorsys.hsv_to_rgb(elt.hue, 1.0, 1.0)
            
            render_y = round(self.matrix_scale * elt.y)
            render_x = round(self.matrix_scale * elt.x)
            
            if 0 <= render_y < self.matrix_height and \
                0 <= render_x < self.matrix_width:
                img[render_y,render_x,:] = rgb
            # Else, skip it
        # Return the vertical flip, origin at the top.
        return np.flipud(img)
    
    def run(self):

        # https://matplotlib.org/stable/gallery/animation/dynamic_image.html

        fig, ax = plt.subplots()
        
        # ims is a list of lists, each row is a list of artists to draw in the
        # current frame; here we are just animating one artist, the image, in
        # each frame
        
        ims = []
        elts = set()

        for i in range(self.steps):
            
            log.info(i)

            
            # log.info(elts)
            
            self.populate_particles()
            self.step(self.dt)
            img = self.render()

            im = ax.imshow(img, animated=True)
            if i == 0:
                ax.imshow(img)  # show an initial one first
            ims.append([im])

        log.info("Animating.")
        interval_ms = int(self.dt * 1000)
        ani = animation.ArtistAnimation(fig, ims, interval=interval_ms, blit=True,
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
    gravity = Gravity(matrix_height=32, matrix_width=32)
    gravity.run()

