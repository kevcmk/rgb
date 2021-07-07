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

    g.midi_handlers({"type": "note_on", "time": 0, "note": 77, "velocity": 66, "channel": 0})
    g.midi_handlers({"type": "note_off", "time": 0, "note": 77, "velocity": 66, "channel": 0})
    g.midi_handlers({"type": "note_on", "time": 0, "note": 81, "velocity": 81, "channel": 0})
    g.midi_handlers({"type": "note_off", "time": 0, "note": 81, "velocity": 81, "channel": 0})
    g.midi_handlers({"type": "note_on", "time": 0, "note": 85, "velocity": 96, "channel": 0})
    g.midi_handlers({"type": "note_off", "time": 0, "note": 85, "velocity": 96, "channel": 0})
    g.midi_handlers({"type": "control_change", "time": 0, "control": 14, "value": 115, "channel": 0})
    g.midi_handlers({"type": "control_change", "time": 0, "control": 14, "value": 114, "channel": 0})
    g.midi_handlers({"type": "control_change", "time": 0, "control": 14, "value": 113, "channel": 0})
    g.midi_handlers({"type": "control_change", "time": 0, "control": 14, "value": 112, "channel": 0})
    g.midi_handlers({"type": "control_change", "time": 0, "control": 14, "value": 111, "channel": 0})
    g.midi_handlers({"type": "note_on", "time": 0, "note": 38, "velocity": 127, "channel": 0})
    g.midi_handlers({"type": "note_off", "time": 0, "note": 38, "velocity": 127, "channel": 0})
    g.midi_handlers({"message": "dial", "index": 0, "state": 0.896498054474708})
    g.midi_handlers({"message": "dial", "index": 0, "state": 0.8789196612497139})

    img_larger = img.resize((img.width * scale, img.height * scale),resample=0).transpose(Image.FLIP_TOP_BOTTOM)
    # img = Image.open("/Users/katz/Pictures/unnamed_b.png")
    # If this image is not here, it will be garbage collected (and will not appear)
    pi = ImageTk.PhotoImage(img_larger)
    canvas.create_image(0,0, anchor=NW, image=pi)      
    canvas.update()
    time.sleep(dt + 500)
# mainloop()   