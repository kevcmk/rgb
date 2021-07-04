from tkinter import *
import os
import sys
import io
from PIL import ImageTk, Image
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from rgb import gravity

hz = 30
dt = 1/hz
scale = 4
matrix_height = 64
matrix_width = 32
g = gravity.Gravity(matrix_height, matrix_width, 0.320, 0.160, 30, 128)

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