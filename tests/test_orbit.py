from tkinter import *
import os
import sys
import io
from PIL import ImageTk, Image
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from rgb import orbit

hz = 30
dt = 1/hz
scale = 4
matrix_height = 64
matrix_width = 32
g = orbit.Orbit(matrix_width=32, matrix_height=64, world_width=1.496e11, world_height=1.496e11 * 2, hz=hz, ffw=86400*60)

root = Tk()      
canvas = Canvas(root, width = matrix_width * scale, height = matrix_height * scale)      
canvas.pack()      

while True:
    img = g.step(dt)
    img_larger = img.resize((img.width * scale, img.height * scale),resample=0).transpose(Image.FLIP_TOP_BOTTOM)
    # img = Image.open("/Users/katz/Pictures/unnamed_b.png")
    # If this image is not here, it will be garbage collected (and will not appear)
    pi = ImageTk.PhotoImage(img_larger)
    canvas.create_image(0,0, anchor=NW, image=pi)      
    canvas.update()
    time.sleep(dt)
# mainloop()   