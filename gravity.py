#!/usr/bin/env python

import random
import json
from typing import List, Set, Tuple
import math
from random import randrange
import time
from samplebase import SampleBase
from dataclasses import dataclass
import colorsys
import logging
import os

import numpy as np

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
    
    @property
    def hsv(self):
        return colorsys.hsv_to_rgb(self.hue, 1.0, 1.0)
    
class Gravity(SampleBase):
    def __init__(self, *args, **kwargs):
        super(Gravity, self).__init__(*args, **kwargs)
        self.hz = 60
        self.steps = 250
        self.world_height: float = 0.320 # Meters 32x5mm
        self.world_width: float = 0.320 # Meters 32x5mm
        self.population = 256
        self.particles: Set[Elt] = set()
    
    def populate_particles(self):
        room = random.randint(0, self.population - len(self.particles))
        for i in range(room):
            self.particles.add(
                Elt(
                    y=self.world_height, 
                    x=random.uniform(0, self.world_width),
                    
                ) 
            )

    @property
    def matrix_height(self) -> int:
        return self.matrix.height
    
    @property
    def matrix_width(self) -> int:
        return self.matrix.width

    @property
    def matrix_scale(self) -> float:
        # E.g. 1:4 would be 0.25
        return self.matrix_height / float(self.world_height)

    @property
    def dt(self):
        return 1 / float(self.hz)
        
    def step(self, dt):
        for elt in self.particles:
            # elt.vy = elt.vy + (-9.8 * dt) # -9.8 m/s^2
            elt.vy = elt.vy + (-1.62 * dt) # Moon gravity
            elt.y = elt.y + (elt.vy * dt)
        self.particles = set(filter(lambda x: x.y >= 0, self.particles))

    def render(self):
        img = np.zeros((self.matrix_height, self.matrix_width, 3))
        for elt in self.particles:
            
            
            render_y = round(self.matrix_scale * elt.y)
            render_x = round(self.matrix_scale * elt.x)
            
            if 0 <= render_y < self.matrix_height and \
                0 <= render_x < self.matrix_width:
                img[render_y,render_x,:] = elt.hsv
            # Else, skip it
        # Return the vertical flip, origin at the top.
        return img
    
    def plot(self):
        
        import matplotlib.pyplot as plt
        import matplotlib.animation as animation
        # https://matplotlib.org/stable/gallery/animation/dynamic_image.html

        fig, ax = plt.subplots()
        
        # ims is a list of lists, each row is a list of artists to draw in the
        # current frame; here we are just animating one artist, the image, in
        # each frame
        
        ims = []
        elts = set()

        for i in range(self.steps):
            
            log.info(i)

            self.populate_particles()
            self.step(self.dt)
            img = self.render()

            # Flip because our plot shows zero at the bottom
            im = ax.imshow(np.flipud(img), animated=True)
            if i == 0:
                ax.imshow(img)  # show an initial one firstx
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

    def run(self):
        log.info("Running...")
        offset_canvas = self.matrix.CreateFrameCanvas()
        while True:
            
            self.populate_particles()
            self.step(self.dt)
            
            # log.info(json.dumps({"matrix_width": self.matrix_width, "matrix_height": self.matrix_height, "img_shape": str(img.shape)}))
        
            offset_canvas.Clear()
            for elt in self.particles:
                render_y = round(self.matrix_scale * elt.y)
                render_x = round(self.matrix_scale * elt.x)
                
                if 0 <= render_y < self.matrix_height and \
                    0 <= render_x < self.matrix_width:
                    rgb = elt.hsv
                    # Set Pixel takes x, y _tf column, row
                    offset_canvas.SetPixel(render_x, render_y, int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
            

            time.sleep(self.dt)
            offset_canvas = self.matrix.SwapOnVSync(offset_canvas)

       


# Main function
if __name__ == "__main__":
    gravity = Gravity()
    if not gravity.process():
        gravity.print_help()

