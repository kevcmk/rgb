from tkinter import *
import os
import sys
import io
from PIL import ImageTk, Image
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from rgb.form import orbit

SECONDS_PER_MONTH = 86400 * 30 # Using this allows us to use 1 month per second
hz = 60
dt = 1/hz
canvas_scale = 6
matrix_height = 64
matrix_width = 32
g = orbit.Orbit((32, 64), fast_forward_scale=1)

root = Tk()      
canvas = Canvas(root, width = matrix_width * canvas_scale, height = matrix_height * canvas_scale)      
canvas.pack()      

while True:
    img = g.step(dt)
    img_larger = img.resize((img.width * canvas_scale, img.height * canvas_scale),resample=0).transpose(Image.FLIP_TOP_BOTTOM)
    
    # If this image is not here, it will be garbage collected (and will not appear)
    pi = ImageTk.PhotoImage(img_larger)
    canvas.create_image(0,0, anchor=NW, image=pi)      
    canvas.update()
    time.sleep(dt)
# mainloop()   