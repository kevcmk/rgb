from tkinter import *
import os
import sys
import io
from PIL import ImageTk, Image
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from rgb import gravity

hz = 30
dt = 1/30
g = gravity.Gravity(64, 32, 0.320, 0.160, 30, 256)
#img = g.step(dt)


root = Tk()      
canvas = Canvas(root, width = 300, height = 300)      
canvas.pack()      


while True:
    #img = g.step(dt)
    img = Image.open("/Users/katz/Pictures/unnamed_b.png")
    pi = ImageTk.PhotoImage(img)
    print(".")
    canvas.create_image(32,64, anchor=NW, image=pi)      
    canvas.update()
    time.sleep(dt)
# mainloop()   