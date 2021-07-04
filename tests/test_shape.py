from tkinter import *
import os
import sys
import io
from PIL import ImageTk, Image
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'rgb')))

from wave import Wave

hz = 1
dt = 1/hz
scale = 4
matrix_height = 160
matrix_width = 32
g = Wave((matrix_width, matrix_height))

root = Tk()      
canvas = Canvas(root, width = matrix_width * scale, height = matrix_height * scale)      
canvas.pack()      

while True:
    img = g.step(dt)
    g.midi_handler({"type": "note_on", "note": 30, "velocity": 127})
    g.midi_handler({"type": "note_on", "note": 32, "velocity": 127})
    g.midi_handler({"type": "note_on", "note": 35, "velocity": 127})
    g.midi_handler({"type": "note_on", "note": 36, "velocity": 127})
    g.midi_handler({"type": "note_on", "note": 40, "velocity": 127})
    img_larger = img.resize((img.width * scale, img.height * scale),resample=0).transpose(Image.FLIP_TOP_BOTTOM)
    # img = Image.open("/Users/katz/Pictures/unnamed_b.png")
    # If this image is not here, it will be garbage collected (and will not appear)
    pi = ImageTk.PhotoImage(img_larger)
    canvas.create_image(0,0, anchor=NW, image=pi)      
    canvas.update()
    time.sleep(dt)
# mainloop()   