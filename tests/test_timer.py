import datetime
import io
import os
import sys
import time
from tkinter import *

from PIL import Image, ImageTk

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from rgb import timer

hz = 30
dt = 1/hz
scale = 4
matrix_height = 64
matrix_width = 32
t = timer.Timer(matrix_height, matrix_width)

root = Tk()      
canvas = Canvas(root, width = matrix_width * scale, height = matrix_height * scale)      
canvas.pack()      

t.t_stop = datetime.datetime.utcnow() + datetime.timedelta(minutes=1, seconds=3)
while True:
    img = t.step(dt)
    img_larger = img.resize((img.width * scale, img.height * scale),resample=0)
    # img = Image.open("/Users/katz/Pictures/unnamed_b.png")
    # If this image is not here, it will be garbage collected (and will not appear)
    pi = ImageTk.PhotoImage(img_larger)
    canvas.create_image(0,0, anchor=NW, image=pi)      
    canvas.update()
    time.sleep(dt)
# mainloop()   
