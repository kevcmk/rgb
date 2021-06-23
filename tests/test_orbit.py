from tkinter import *
import os
import sys
import io
from PIL import ImageTk, Image
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from rgb import orbit

SECONDS_PER_DAY = 86400 # Using this allows us to use 1 month per second
hz = 30
dt = 1/hz
canvas_scale = 6
matrix_height = 64
matrix_width = 32
g = orbit.Orbit(matrix_width=32, matrix_height=64, hz=hz, ffw=SECONDS_PER_DAY)

root = Tk()      
canvas = Canvas(root, width = matrix_width * canvas_scale, height = matrix_height * canvas_scale)      
canvas.pack()      

while True:
    img = g.step(dt)
    # img_larger = img.resize((img.width * canvas_scale, img.height * canvas_scale),resample=0).transpose(Image.FLIP_TOP_BOTTOM)
    # img = Image.open("/Users/katz/Pictures/unnamed_b.png")
    # If this image is not here, it will be garbage collected (and will not appear)
    # pi = ImageTk.PhotoImage(img_larger)
    #canvas.create_image(0,0, anchor=NW, image=pi)      
    #canvas.update()
    # time.sleep(dt)
# mainloop()   